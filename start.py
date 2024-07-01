import asyncio
import concurrent.futures
import json
import os
import platform
import socket
import sys
import time

import schedule
import yaml
from loguru import logger
from uvicorn import Config, Server

import pywxdll
import utils.xybot as xybot
from utils.plans_manager import plan_manager
from utils.plugin_manager import plugin_manager
from utils.web_api import app
from utils.web_api_data import WebApiData


async def start_api_server():
    # 重置连续运行天数为0
    web_api_data = WebApiData()
    web_api_data.update_data('running_days', 0)

    config = Config(app, loop='none')
    server = Server(config)
    await server.serve()


async def message_handler(client_socket, handlebot, web_api_data):  # 处理收到的消息
    message = b""
    while True:
        message += await asyncio.get_running_loop().sock_recv(client_socket, 1024)
        if len(message) == 0 or message[-1] == 0xA:
            break
    client_socket.close()
    message_json = json.loads(message.decode('utf-8'))
    logger.info(f"[收到消息]:{message_json}")
    web_api_data.update_data('received_message_count', web_api_data.get_data()['received_message_count'] + 1)

    await asyncio.create_task(handlebot.message_handler(message_json))


def callback(worker):  # 处理线程结束时，有无错误
    worker_exception = worker.exception()
    if worker_exception:
        logger.error(worker_exception)


async def plan_run_pending():  # 计划等待判定线程
    logger.debug("开始计划等待判定线程")
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


async def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # ---- log设置 读取设置 ---- #
    logger.add(
        "logs/log_{time}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        encoding="utf-8",
        enqueue=True,
        retention="2 weeks",
        rotation="00:01",
    )  # 日志设置
    logger.info("已设置日志")

    with open("main_config.yml", "r", encoding="utf-8") as f:  # 读取设置
        config = yaml.safe_load(f.read())

    ip = config["ip"]
    port = config["port"]
    tcp_server_port = config["tcp_server_port"]

    max_worker = config["max_worker"]

    logger.info("读取设置成功")

    # ---- 微信Hook注入 修复微信版本过低问题 机器人实例化 登陆监测 机器人启动 ---- #

    bot = pywxdll.Pywxdll(ip, port)
    logger.info("机器人实例化成功")

    # 微信Hook注入
    logger.info("开始注入Hook")
    possible_error = ''
    system = platform.system()
    if platform.architecture()[0] != "64bit":
        possible_error = "不支持的操作系统，需要64位。"
    elif not (sys.maxsize > 2 ** 32):
        possible_error = "需要64位Python。"
    elif system != "Windows" and system != "Linux":
        possible_error = f"不支持的操作系统: {system}"

    if possible_error:
        logger.error(possible_error)
        sys.exit(1)

    inject_result = False
    if system == "Windows":
        inject_result = bot.windows_start_wechat_and_inject()
    elif system == "Linux":
        inject_result = bot.docker_inject_dll()

    time.sleep(1)  # 等待注入完毕
    if inject_result:
        logger.info("已注入微信Hook")
    else:
        logger.error("注入微信Hook失败！")
        sys.exit(1)

    # 修复微信版本过低问题
    if not bot.is_logged_in():
        if bot.fix_wechat_version():
            logger.info("已修复微信版本过低问题")
        else:
            logger.error("修复微信版本过低问题失败！")
            sys.exit(1)
    else:
        logger.info("已登陆，不需要修复微信版本过低问题")

    # 检查是否登陆了微信
    logger.info("开始检测微信是否登陆")
    while not bot.is_logged_in():
        logger.warning("机器人微信账号未登录！请扫码登陆微信。")
        time.sleep(3)

    logger.success("已确认微信已登陆，开始启动XYBot")

    asyncio.create_task(start_api_server()).add_done_callback(callback)  # 开启web api服务
    web_api_data = WebApiData()

    handlebot = xybot.XYBot()

    # ---- 加载插件 加载计划 ---- #

    # 加载所有插件
    plugin_manager.load_plugins()  # 加载所有插件
    logger.info("已加载所有插件")

    plans_dir = "plans"
    plan_manager.load_plans(plans_dir)  # 加载所有计划

    asyncio.create_task(plan_run_pending()).add_done_callback(callback)  # 开启计划等待判定线程
    logger.info("已加载所有计划，并开始后台运行")

    # ---- 启动tcp服务器并开始接受处理消息 ---- #
    bot.start_hook_msg(tcp_server_port, '127.0.0.1')

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setblocking(False)
    server_socket.bind(('127.0.0.1', tcp_server_port))
    server_socket.listen(max_worker)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_worker):
        logger.success("机器人启动成功！")
        logger.debug(f"线程池大小应为{max_worker}")

        while True:
            try:
                client_socket, address = await asyncio.get_running_loop().sock_accept(server_socket)
                client_socket.setblocking(False)

                asyncio.create_task(message_handler(client_socket, handlebot, web_api_data)).add_done_callback(callback)
            except Exception as error:
                logger.error(f"出现错误: {error}")


if __name__ == "__main__":
    asyncio.run(main())
