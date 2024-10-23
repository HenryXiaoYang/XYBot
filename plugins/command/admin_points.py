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


class admin_points(PluginInterface):
    def __init__(self):
        config_path = "plugins/command/admin_points.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取插件设置
            config = yaml.safe_load(f.read())

        self.command_format_menu = config["command_format_menu"]  # 获取指令格式

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.admin_list = main_config["admins"]  # 获取管理员列表
        self.db = BotDatabase()  # 实例化数据库类

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        recv.content = re.split(" ", recv.content)  # 拆分消息

        admin_wxid = recv.sender  # 获取发送者wxid

        error = ''
        if admin_wxid not in self.admin_list:
            error = "-----XYBot-----\n❌你配用这个指令吗？"
        elif len(recv.content) < 3:
            error = f"-----XYBot-----\n⚠️指令格式错误！\n\n{self.command_format_menu}"
        elif recv.content[1] not in ["加", "减"] and not recv.content[1].isnumeric():
            error = f"-----XYBot-----\n⚠️指令格式错误！\n\n{self.command_format_menu}"

        if not error:

            if recv.content[1].isnumeric():  # 直接改变，不加/减
                if recv.content[2].startswith('@') and recv.ats:  # 判断是@还是wxid
                    change_wxid = recv.ats[-1]
                else:
                    change_wxid = recv.content[2]

                self.db.set_points(change_wxid, int(recv.content[1]))

                nickname = self.db.get_nickname(change_wxid)  # 尝试获取昵称

                out_message = f'-----XYBot-----\n😊成功将 {change_wxid} {nickname if nickname else ""} 的积分设置为 {recv.content[1]}！'
                await self.send_friend_or_group(bot, recv, out_message)


            elif recv.content[1] == "加":  # 操作是加分
                if recv.content[3].startswith('@') and recv.ats:  # 判断是@还是wxid
                    change_wxid = recv.ats[-1]
                else:
                    change_wxid = recv.content[3]

                self.db.add_points(change_wxid, int(recv.content[2]))  # 修改积分

                nickname = self.db.get_nickname(change_wxid)  # 尝试获取昵称
                new_point = self.db.get_points(change_wxid)  # 获取修改后积分

                out_message = f'-----XYBot-----\n😊成功给 {change_wxid} {nickname if nickname else ""} 加了 {recv.content[2]} 点积分，他现在有 {new_point} 点积分！'
                await self.send_friend_or_group(bot, recv, out_message)

            elif recv.content[1] == "减":  # 操作是减分
                if recv.content[3].startswith('@'):  # 判断是@还是wxid
                    change_wxid = recv.ats[-1]
                else:
                    change_wxid = recv.content[3]

                self.db.add_points(change_wxid, int(recv.content[2]) * -1)  # 修改积分

                nickname = self.db.get_nickname(change_wxid)  # 尝试获取昵称
                new_point = self.db.get_points(change_wxid)  # 获取修改后积分

                out_message = f'-----XYBot-----\n😊成功给 {change_wxid} {nickname if nickname else ""} 减了 {recv.content[2]} 点积分，他现在有 {new_point} 点积分！'
                await self.send_friend_or_group(bot, recv, out_message)

            else:
                error = f"-----XYBot-----\n\n⚠️指令格式错误！\n{self.command_format_menu}"
                logger.info(f'[发送信息]{error}| [发送到] {recv.roomid}')
                bot.send_text(error, recv.roomid)


        else:  # 发送错误信息
            out_message = error
            logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid)

    async def send_friend_or_group(self, bot: client.Wcf, recv: XYBotWxMsg, out_message="null"):
        if recv.from_group():  # 判断是群还是私聊
            out_message = f"@{self.db.get_nickname(recv.sender)}\n{out_message}"
            logger.info(f'[发送@信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid, recv.sender)  # 发送@信息

        else:
            logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid)  # 发送
