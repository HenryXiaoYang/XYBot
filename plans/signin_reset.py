import os

import pywxdll
import yaml
from loguru import logger

import database
from plans_interface import PlansInterface


class signin_reset(PlansInterface):
    def __init__(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.ip = main_config['ip']
        self.port = main_config['port']
        self.timezone = main_config['plan_timezone']
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api
        self.bot.start()  # 开启机器人

    def job(self):
        db = database.BotDatabase()
        db.reset_stat()
        logger.info('[数据库]签到状态重置成功！')

    def run(self, myscheduler):
        myscheduler.every().day.at("03:00", self.timezone).do(self.job)  # 重置签到时间
