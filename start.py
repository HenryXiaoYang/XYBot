import asyncio
import concurrent.futures
import json
import os
import time

import schedule
import websockets
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


async def message_handler(recv, handlebot):  # 处理收到的消息
    await asyncio.create_task(handlebot.message_handler(recv))


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

    max_worker = config["max_worker"]

    logger.info("读取设置成功")

    # ---- 机器人实例化 登陆监测 机器人启动 ---- #

    bot = pywxdll.Pywxdll(ip, port)
    logger.info("机器人实例化成功")

    # 检查是否登陆了微信
    logger.info("开始检测微信是否登陆")
    logged_in = False
    while not logged_in:
        try:
            if bot.get_personal_detail("filehelper"):
                logged_in = True
                logger.success("机器人微信账号已登录！")
        except:
            logger.warning(
                f"机器人微信账号未登录！请使用浏览器访问 http://{ip}:4000/vnc.html 扫码登陆微信"
            )
            time.sleep(3)
    logger.info("已确认微信已登陆，开始启动XYBot")

    bot.start()  # 开启机器人

    asyncio.create_task(start_api_server()).add_done_callback(callback)  # 开启web api服务
    web_api_data = WebApiData()

    handlebot = xybot.XYBot()

    # ---- 加载插件 加载计划 ---- #

    # 加载所有插件
    plugin_manager.load_plugins()  # 加载所有插件
    logger.info("已加载所有插件")

    plans_dir = "plans"
    plan_manager.load_plans(plans_dir)  # 加载所有计划

    asyncio.create_task(plan_run_pending()).add_done_callback(
        callback
    )  # 开启计划等待判定线程
    logger.info("已加载所有计划，并开始后台运行")

    # ---- 进入获取聊天信息并处理循环 ---- #
    async with websockets.connect(f"ws://{ip}:{port}") as websocket:
        logger.success("机器人启动成功！")
        logger.debug(f"线程池大小应为{max_worker}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_worker):
            while True:
                try:
                    recv = json.loads(await websocket.recv())
                    r_type = recv["type"]
                    if r_type == 1 or r_type == 3 or r_type == 49:
                        logger.info(f"[收到消息]:{recv}")
                        web_api_data.update_data('received_message_count',
                                                 web_api_data.get_data()['received_message_count'] + 1)
                        if isinstance(recv["content"], str):  # 判断是否为txt消息
                            asyncio.create_task(
                                message_handler(recv, handlebot)
                            ).add_done_callback(callback)
                except Exception as error:
                    logger.error(f"出现错误: {error}")


if __name__ == "__main__":
    asyncio.run(main())
