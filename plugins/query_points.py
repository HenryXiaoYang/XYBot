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
        if recv["id1"]:  # 判断是群还是私聊
            query_wxid = recv["id1"]  # 是群
        else:
            query_wxid = recv["wxid"]  # 是私聊

        nickname = self.bot.get_chatroom_nickname(recv["wxid"], recv["id1"])[
            "nick"
        ]  # 获取昵称

        out_message = f"-----XYBot-----\n你有{self.db.get_points(query_wxid)}点积分！👍"  # 从数据库获取积分数并创建信息
        logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
        self.bot.send_at_msg(recv["wxid"], recv["id1"], nickname, out_message)  # 发送
