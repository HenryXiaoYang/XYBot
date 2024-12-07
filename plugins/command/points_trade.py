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


class points_trade(PluginInterface):
    def __init__(self):
        config_path = "plugins/command/points_trade.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.command_format_menu = config["command_format_menu"]  # 指令格式

        self.max_points = config["max_points"]  # 最多转帐多少积分
        self.min_points = config["min_points"]  # 最少转帐多少积分

        self.db = BotDatabase()  # 实例化机器人数据库类

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        recv.content = re.split(" |\u2005", recv.content)  # 拆分消息

        if recv.from_group() and len(recv.content) >= 3 and recv.content[1].isdigit():  # 判断是否为转账指令
            roomid, trader_wxid = recv.roomid, recv.sender  # 获取群号和转账人wxid

            target_wxid = recv.ats[0]  # 获取转账目标wxid

            points_num = recv.content[1]  # 获取转账积分数

            error_message = self.get_error_message(
                target_wxid, trader_wxid, points_num
            )  # 获取是否有错误信息

            if not error_message:  # 判断是否有错误信息和是否转账成功
                points_num = int(points_num)
                self.db.safe_trade_points(trader_wxid, target_wxid, points_num)
                # 记录日志和发送成功信息
                await self.log_and_send_success_message(bot, roomid, trader_wxid, target_wxid, points_num)
                bot.send_pat_msg(roomid, target_wxid)
            else:
                await self.log_and_send_error_message(bot, roomid, trader_wxid, error_message)  # 记录日志和发送错误信息
        else:
            out_message = f"@{self.db.get_nickname(recv.sender)}\n-----XYBot-----\n转帐失败❌\n指令格式错误/在私聊转帐积分(仅可在群聊中转帐积分)❌\n\n{self.command_format_menu}"
            logger.info(f'[发送@信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid, recv.sender)

    def get_error_message(self, target_wxid, trader_wxid, points_num: str):  # 获取错误信息
        if not target_wxid:
            return "\n-----XYBot-----\n转帐失败❌\n转帐人不存在"
        elif not points_num.isdigit():
            return "\n-----XYBot-----\n转帐失败❌\n转帐积分无效(必须为正整数!)"
        points_num = int(points_num)
        if not self.min_points <= points_num <= self.max_points:
            return f"\n-----XYBot-----\n转帐失败❌\n转帐积分无效(最大{self.max_points} 最小{self.min_points})"
        elif self.db.get_points(trader_wxid) < points_num:
            return f"\n-----XYBot-----\n积分不足！❌\n需要{points_num}点！"

    # 记录日志和发送成功信息
    async def log_and_send_success_message(self, bot: client.Wcf, roomid, trader_wxid, target_wxid, points_num):
        trader_nick = bot.get_alias_in_chatroom(trader_wxid, roomid)  # 获取转账人昵称
        target_nick = bot.get_alias_in_chatroom(target_wxid, roomid)  # 获取转账目标昵称

        logger.success(
            f"[积分转帐]转帐人:{trader_wxid} {trader_nick}|目标:{target_wxid} {target_nick}|群:{roomid}|积分数:{points_num}"
        )
        trader_points, target_points = self.db.get_points(trader_wxid), self.db.get_points(target_wxid)
        out_message = f"@{trader_nick} @{target_nick}\n-----XYBot-----\n转帐成功✅! 你现在有{trader_points}点积分 {target_nick}现在有{target_points}点积分"
        logger.info(f'[发送@信息]{out_message}| [发送到] {roomid}')
        bot.send_text(out_message, roomid, ",".join([trader_wxid, target_wxid]))

    async def log_and_send_error_message(self, bot: client.Wcf, roomid, trader_wxid, error_message):  # 记录日志和发送错误信息
        error_message = f"@{self.db.get_nickname(trader_wxid)}\n{error_message}"
        logger.info(f'[发送@信息]{error_message}| [发送到] {roomid}')
        bot.send_text(error_message, roomid, trader_wxid)
