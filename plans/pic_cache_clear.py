import os

import pywxdll
import schedule
import yaml
from loguru import logger

from plans_interface import PlansInterface


class pic_cache_clear(PlansInterface):
    def __init__(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.ip = main_config['ip']
        self.port = main_config['port']
        self.timezone = main_config['timezone']
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api
        self.bot.start()  # 开启机器人

    def job(self):
        path = '../resources/pic_cache/'
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            # 判断路径是否为文件
            if os.path.isfile(file_path):
                # 删除文件
                os.remove(file_path)

        logger.info('[计划]清除随机图图缓存成功')

    def run(self):
        schedule.every(60).minutes.do(self.job)
