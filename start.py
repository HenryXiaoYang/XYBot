import os
import time
from concurrent.futures import ThreadPoolExecutor

import pywxdll
import schedule
import yaml
from loguru import logger

import xybot
from plans_manager import plan_manager
from plugin_manager import plugin_manager


def message_handler(recv):
    handlebot = xybot.XYBot()
    handlebot.message_handler(recv)


def threadpool_callback(worker):
    worker_exception = worker.exception()
    if worker_exception:
        logger.error(worker_exception)


if __name__ == "__main__":
    logger.add('logs/log_{time}.log', encoding='utf-8', enqueue=True, retention='2 weeks', rotation='00:01')  # 日志设置

    pic_cache_path = './pic_cache'  # 检测是否有pic_cache文件夹
    if not os.path.exists(pic_cache_path):
        logger.info('检测到未创建pic_cache图片缓存文件夹')
        os.makedirs(pic_cache_path)
        logger.info('已创建pic_cach文件夹')

    with open('main_config.yml', 'r', encoding='utf-8') as f:  # 读取设置
        config = yaml.load(f.read(), Loader=yaml.FullLoader)

    ip = config['ip']
    port = config['port']

    bot = pywxdll.Pywxdll(ip, port)

    # 检查是否登陆了微信
    logged_in = False
    while not logged_in:
        try:
            if bot.get_personal_detail('filehelper'):
                logged_in = True
                logger.success('机器人微信账号已登录！')
        except:
            logger.warning('机器人微信账号未登录！请使用浏览器访问 http://{ip}:4000/vnc.html 登陆微信'.format(ip=ip))
            time.sleep(3)

    bot.start()  # 开启机器人

    # 加载所有插件
    plugin_dir = "plugins"  # 插件目录的路径
    plugin_manager.load_plugins(plugin_dir)  # 加载所有插件

    myscheduler = schedule.Scheduler()
    plans_dir = "plans"
    plan_manager.load_plans(plans_dir, myscheduler)  # 加载所有计划

    pool = ThreadPoolExecutor(max_workers=25, thread_name_prefix='xybot')  # 创建线程池

    logger.success('机器人启动成功！')
    while True:
        if len(bot.msg_list) != 0:  # 如果有聊天信息
            recv = bot.msg_list.pop(0)  # 获取信息列表第一项并pop
            logger.info('[收到消息]:{command}'.format(command=recv))
            try:
                pool.submit(message_handler, recv).add_done_callback(threadpool_callback)  # 向线程池提交任务
            except Exception as error:  # 异常处理
                logger.error(error)
                bot.send_txt_msg(recv['wxid'], '出现错误！⚠️{error}'.format(error=error))

        myscheduler.run_pending()
