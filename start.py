import os
from concurrent.futures import ThreadPoolExecutor

import pywxdll
import schedule
import yaml
from loguru import logger

import database
import xybot


def handle_bot(recv):  # 处理聊天
    handlebot = xybot.XYBot()
    handlebot.handle_message(recv)


def reset_signinstat():  # 签到状态重置
    db = database.BotDatabase()
    db.reset_stat()
    logger.info('[数据库]签到状态重置成功！')


def schedule_antiautolog():  # 防微信自动退出
    handlebot = xybot.XYBot()
    handlebot.schudle_antiautolog_handler()


if __name__ == "__main__":
    with open('config.yml', 'r', encoding='utf-8') as f:  # 读取设置
        config = yaml.load(f.read(), Loader=yaml.FullLoader)
    logger.add('logs/log_{time}.log', encoding='utf-8', enqueue=True, compression='zip', retention='2 weeks',
               rotation='00:01')  # 日志设置

    pic_cache_path = './pic_cache'  # 检测是否有pic_cache文件夹
    if not os.path.exists(pic_cache_path):
        logger.info('检测到未创建pic_cache图片缓存文件夹')
        os.makedirs(pic_cache_path)
        logger.info('已创建pic_cach文件夹')

    log_path = './logs'  # 检查是否有logs文件夹，在设置log时应就被创建，这里的是一个backup
    if not os.path.exists(log_path):
        logger.info('检测到未创建logs日志文件夹')
        os.makedirs(log_path)
        logger.info('已创建log文件夹')

    ip = config['ip']
    port = config['port']

    logger.info('微信机器人，启动！')
    bot = pywxdll.Pywxdll(ip, port)
    bot.start()  # 开启机器人
    logger.info('机器人启动成功！')

    schedule.every().day.at("03:00").do(reset_signinstat)  # 重置签到时间
    schedule.every(30).minutes.do(schedule_antiautolog)  # 防微信自动退出登录

    pool = ThreadPoolExecutor(max_workers=15)  # 创建线程池
    while True:
        schedule.run_pending()
        if len(bot.msg_list) != 0:  # 如果有聊天信息
            recv = bot.msg_list.pop(0)  # 获取信息列表第一项并pop
            logger.info('[收到消息]:{command}'.format(command=recv))
            pool.submit(handle_bot, recv)  # 向线程池提交任务
