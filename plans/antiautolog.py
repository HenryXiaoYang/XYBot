import os
import random

import pywxdll
import schedule
import yaml
from loguru import logger

from plans_interface import PlansInterface


class antiautolog(PlansInterface):
    def __init__(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.ip = main_config['ip']
        self.port = main_config['port']
        self.timezone = main_config['timezone']
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

    def job(self):
        out_message = '防微信自动退出登录[{num}]'.format(num=random.randint(1, 9999))  # 组建信息
        logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message,
                                                                      wxid="filehelper"))  # 直接发到文件传输助手，这样就不用单独键个群辣
        self.bot.send_txt_msg("filehelper", out_message)  # 发送

    def run(self):
        schedule.every(10).minutes.do(self.job)  # 每10分钟执行一次
