#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import yaml
from loguru import logger

import pywxdll
from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface


class admin_signin_reset(PluginInterface):
    def __init__(self):
        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config["ip"]  # 获取机器人api的ip
        self.port = main_config["port"]  # 获取机器人api的端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

        self.admin_list = main_config["admins"]  # 获取管理员列表

        self.db = BotDatabase()  # 实例化数据库类

    async def run(self, recv):
        admin_wxid = recv["sender"]

        if admin_wxid in self.admin_list:  # 如果操作人在白名单内
            self.db.reset_stat()  # 重置数据库签到状态
            out_message = "-----XYBot-----\n😊成功重置签到状态！"
            logger.info(f'[发送信息]{out_message}| [发送到] {recv["from"]}')
            await self.bot.send_text_msg(recv["from"], out_message)  # 发送信息

        else:  # 操作人不在白名单内
            out_message = "-----XYBot-----\n❌你配用这个指令吗？"
            logger.info(f'[发送信息]{out_message}| [发送到] {recv["from"]}')
            await self.bot.send_text_msg(recv["from"], out_message)  # 发送信息
