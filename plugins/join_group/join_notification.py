#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.
import os
import re

from loguru import logger
from wcferry import client

from utils.plugin_interface import PluginInterface
from wcferry_helper import XYBotWxMsg


class join_notification(PluginInterface):
    def __init__(self):
        self.logo_path = os.path.abspath("resources/XYBotLogo.png")

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        join_group_msg = recv.content

        # 邀请进来的
        if "邀请" in join_group_msg:
            # 通过正则表达式提取邀请者的名字
            invite_pattern = r'"([^"]+)"邀请"([^"]+)"加入了群聊'
            match = re.search(invite_pattern, join_group_msg)

            if match:
                joiner = match.group(2)
                await self.send_welcome(bot, recv.roomid, joiner)

    async def send_welcome(self, bot: client.Wcf, roomid: str, joiner: str):
        out_message = f"-------- XYBot ---------\n👏欢迎新成员 {joiner} 加入本群！⭐️\n⚙️输入 菜单 获取玩法哦😄"
        logger.info(f'[发送信息]{out_message}| [发送到] {roomid}')
        bot.send_text(out_message, roomid)
