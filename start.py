import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pywxdll
import schedule
import yaml
from loguru import logger

import xybot
from plans_manager import plan_manager
from plugin_manager import plugin_manager


def message_handler(recv):  # 处理收到的消息
    handlebot = xybot.XYBot()
    handlebot.message_handler(recv)


def threadpool_callback(worker):  # 处理线程结束时，有无错误
    worker_exception = worker.exception()
    if worker_exception:
        logger.error(worker_exception)


def schedule_run_pending():  # 计划等待判定线程
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    ###### log设置 读取设置 ######
    logger.add('logs/log_{time}.log', encoding='utf-8', enqueue=True, retention='2 weeks', rotation='00:01')  # 日志设置

    pic_cache_path = 'resources/pic_cache'  # 检测是否有pic_cache文件夹
    if not os.path.exists(pic_cache_path):
        logger.info('检测到未创建pic_cache图片缓存文件夹')
        os.makedirs(pic_cache_path)
        logger.info('已创建pic_cach文件夹')

    with open('main_config.yml', 'r', encoding='utf-8') as f:  # 读取设置
        config = yaml.load(f.read(), Loader=yaml.FullLoader)

    ip = config['ip']
    port = config['port']

    max_thread = config['max_thread']

    ###### 机器人实例化 登陆监测 机器人启动 ######

    bot = pywxdll.Pywxdll(ip, port)

    # 检查是否登陆了微信
    logged_in = False
    while not logged_in:
        try:
            if bot.get_personal_detail('filehelper'):
                logged_in = True
                logger.success('机器人微信账号已登录！')
        except:
            logger.warning('机器人微信账号未登录！请使用浏览器访问 http://{ip}:4000/vnc.html 扫码登陆微信'.format(ip=ip))
            time.sleep(3)

    bot.start()  # 开启机器人

    ###### 加载插件 加载计划 ######

    # 加载所有插件
    plugin_dir = "plugins"  # 插件目录的路径
    plugin_manager.load_plugins(plugin_dir)  # 加载所有插件

    plans_dir = "plans"
    plan_manager.load_plans(plans_dir)  # 加载所有计划

    ###### 线程池创建 计划等待判定线程创建与启动 ######

    pool = ThreadPoolExecutor(max_workers=max_thread, thread_name_prefix='xybot')  # 创建线程池

    run_pending_thread = threading.Thread(target=schedule_run_pending)
    run_pending_thread.start()

    ####### 进入获取聊天信息并处理循环 ######

    logger.success('机器人启动成功！')
    while True:
        try:
            if len(bot.msg_list) != 0:  # 如果有聊天信息
                recv = bot.msg_list.pop(0)  # 获取信息列表第一项并pop
                logger.info('[收到消息]:{message}'.format(message=recv))
                if isinstance(recv['content'], str):  # 判断是否为txt消息
                    pool.submit(message_handler, recv).add_done_callback(threadpool_callback)  # 向线程池提交任务
        except:
            logger.warning('机器人微信账号未登录！请使用浏览器访问 http://{ip}:4000/vnc.html 扫码登陆微信'.format(ip=ip))
            time.sleep(3)
