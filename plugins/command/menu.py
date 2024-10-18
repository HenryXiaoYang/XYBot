#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import yaml
from loguru import logger
from wcferry import client

from utils.plugin_interface import PluginInterface
from wcferry_helper import XYBotWxMsg


class menu(PluginInterface):
    def __init__(self):
        config_path = "plugins/command/menu.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.main_menu = config["main_menu"]
        self.menus = config["menus"]

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        recv.content = recv.content.split(" |\u2005")  # 拆分消息

        if len(recv.content) == 1:  # 如果命令列表长度为1，那就代表请求主菜单
            out_message = self.main_menu
            logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid)

        elif recv.content[1] in self.menus.keys():  # 长度不为1，发送以参数为键菜单内容为值的字典
            out_message = self.menus[recv.content[1]]
            logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid)

        else:
            out_message = "找不到此菜单!⚠️"  # 没找到对应菜单，发送未找到
            logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid)
