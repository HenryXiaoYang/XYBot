import os

import schedule
import yaml
from loguru import logger

import pywxdll
from utils.plans_interface import PlansInterface


class pic_cache_clear(PlansInterface):
    def __init__(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, "../main_config.yml")
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config["ip"]  # 机器人ip
        self.port = main_config["port"]  # 机器人端口
        self.timezone = main_config["timezone"]  # 时区
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

    def job(self):
        path = "./resources/pic_cache/"  # 图片缓存路径
        for filename in os.listdir(path):  # 遍历文件夹
            file_path = os.path.join(path, filename)  # 获取文件路径
            # 判断路径是否为文件
            if os.path.isfile(file_path):  # 如果是文件
                # 删除文件
                os.remove(file_path)

        logger.info("[计划]清除随机图图缓存成功")  # 记录日志

    def run(self):
        schedule.every(60).minutes.do(self.job)  # 每60分钟执行一次
