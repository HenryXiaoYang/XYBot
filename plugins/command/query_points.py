#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import yaml
from loguru import logger

import pywxdll
from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface


class query_points(PluginInterface):
    def __init__(self):
        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config["ip"]  # 机器人ip
        self.port = main_config["port"]  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

        self.db = BotDatabase()  # 实例化机器人数据库类

    async def run(self, recv):
        query_wxid = recv["sender"]

        points_count = self.db.get_points(query_wxid)

        out_message = f"-----XYBot-----\n你有{points_count}点积分！👍"  # 从数据库获取积分数并创建信息
        logger.info(f'[发送@信息]{out_message}| [发送到] {recv["from"]}')
        self.bot.send_at_msg(recv["from"], out_message, [query_wxid])
