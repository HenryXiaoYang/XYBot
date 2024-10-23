#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import re

import yaml
from loguru import logger
from wcferry import client

from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface
from wcferry_helper import XYBotWxMsg


class admin_whitelist(PluginInterface):
    def __init__(self):
        config_path = "plugins/command/admin_whitelist.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取插件设置
            config = yaml.safe_load(f.read())

        self.command_format_menu = config["command_format_menu"]  # 获取命令格式

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.admin_list = main_config["admins"]  # 获取管理员列表

        self.db = BotDatabase()  # 实例化数据库类

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        recv.content = re.split(" ", recv.content)  # 拆分消息
        logger.debug(recv.content)

        admin_wxid = recv.sender  # 获取发送者wxid

        error = ""
        if admin_wxid not in self.admin_list:  # 判断是否为管理员
            error = "-----XYBot-----\n❌你配用这个指令吗？"
        elif len(recv.content) < 3:  # 判断命令格式是否正确
            error = f"-----XYBot-----\n命令格式错误❌\n\n{self.command_format_menu}"

        if not error:
            if recv.content[2].startswith("@") and recv.ats:
                wxid = recv.ats[-1]
            else:
                wxid = recv.content[2]

            if recv.content[1] == "加入":
                self.db.set_whitelist(wxid, 1)

                nickname = self.db.get_nickname(wxid) # 尝试获取昵称

                out_message = f"-----XYBot-----\n成功添加 {wxid} {nickname if nickname else ""} 到白名单！😊"
                await self.send_friend_or_group(bot, recv, out_message)

            elif recv.content[1] == "移除":
                self.db.set_whitelist(wxid, 0)

                nickname = self.db.get_nickname(wxid)  # 尝试获取昵称

                out_message = f"-----XYBot-----\n成功把 {wxid} {nickname if nickname else ""} 移出白名单！😊"
                await self.send_friend_or_group(bot, recv, out_message)

            else:
                error = f"-----XYBot-----\n未知的操作❌\n\n{self.command_format_menu}"
                await self.send_friend_or_group(bot, recv, error)
        else:
            await self.send_friend_or_group(bot, recv, error)



    async def send_friend_or_group(self, bot: client.Wcf, recv: XYBotWxMsg, out_message="null"):
        if recv.from_group():  # 判断是群还是私聊
            out_message = f"@{self.db.get_nickname(recv.sender)}\n{out_message}"
            logger.info(f'[发送@信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid, recv.sender)  # 发送@信息

        else:
            logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid)  # 发送
