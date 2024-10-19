#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import re

from loguru import logger
from wcferry import client

from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface
from wcferry_helper import XYBotWxMsg


class query_points(PluginInterface):
    def __init__(self):
        self.db = BotDatabase()  # 实例化机器人数据库类

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        recv.content = re.split(" |\u2005", recv.content)  # 拆分消息

        query_wxid = recv.sender  # 获取查询wxid

        points_count = self.db.get_points(query_wxid)

        out_message = f"@{self.db.get_nickname(query_wxid)}\n-----XYBot-----\n你有{points_count}点积分！👍"  # 从数据库获取积分数并创建信息
        logger.info(f'[发送@信息]{out_message}| [发送到] {recv.roomid}')
        bot.send_text(out_message, recv.roomid, query_wxid)
