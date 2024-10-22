#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.


import re

from loguru import logger
from wcferry import client

from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface
from wcferry_helper import XYBotWxMsg


class at_test(PluginInterface):
    def __init__(self):
        self.db = BotDatabase()

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        recv.content = re.split(" |\u2005", recv.content)  # 拆分消息

        out_message = f"@{self.db.get_nickname(recv.sender)} At test!!!"
        logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
        bot.send_text(out_message, recv.roomid, recv.sender)

        out_message = str(recv.content)
        logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
        bot.send_text(out_message, recv.roomid)
