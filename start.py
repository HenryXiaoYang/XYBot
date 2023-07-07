from concurrent.futures import ThreadPoolExecutor

import pywxdll
import schedule
import yaml
from loguru import logger

import database
import xybot


def handle_bot(recv):
    handlebot = xybot.XYBot()
    handlebot.handle_message(recv)


def reset_signinstat():
    db = database.BotDatabase()
    db.reset_stat()
    logger.info('[数据库]签到重置成功！')


if __name__ == "__main__":
    with open('config.yml', 'r', encoding='utf-8') as f:  # 读取设置
        config = yaml.load(f.read(), Loader=yaml.FullLoader)
    logger.add('logs/log_{time}.log', encoding='utf-8', enqueue=True, compression='zip', retention='2 weeks', rotation='00:01')

    ip = config['ip']
    port = config['port']

    logger.info('微信机器人，启动！')
    bot = pywxdll.Pywxdll(ip, port)
    bot.start()  # 开启机器人
    logger.info('机器人启动成功！')

    schedule.every().day.at("03:00").do(reset_signinstat)  # 重置签到时间

    pool = ThreadPoolExecutor(max_workers=10)
    while True:
        schedule.run_pending()
        if len(bot.msg_list) != 0:
            recv = bot.msg_list.pop(0)  # 获取信息列表第一项并pop
            logger.info('[收到消息]:{command}'.format(command=recv))
            pool.submit(handle_bot, recv)
