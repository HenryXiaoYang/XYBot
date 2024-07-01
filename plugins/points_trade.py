import yaml
from loguru import logger

import pywxdll
from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface


class points_trade(PluginInterface):
    def __init__(self):
        config_path = "plugins/points_trade.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.max_points = config["max_points"]  # 最多转帐多少积分
        self.min_points = config["min_points"]  # 最少转帐多少积分

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config["ip"]  # 机器人ip
        self.port = main_config["port"]  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

        self.db = BotDatabase()  # 实例化机器人数据库类

    async def run(self, recv):
        if (recv["fromType"] == 'chatroom' and len(recv["content"]) >= 3 and recv["content"][1].isdigit()):  # 判断是否为转账指令
            roomid, trader_wxid = recv["from"], recv["sender"]  # 获取群号和转账人wxid

            target_wxid = recv['atUserList'][0]  # 获取转账目标wxid

            points_num = recv["content"][1]  # 获取转账积分数

            error_message = self.get_error_message(
                target_wxid, trader_wxid, points_num
            )  # 获取是否有错误信息

            if not error_message:  # 判断是否有错误信息和是否转账成功
                points_num = int(points_num)
                self.db.safe_trade_points(trader_wxid, target_wxid, points_num)
                self.log_and_send_success_message(
                    roomid,
                    trader_wxid,
                    target_wxid,
                    points_num,
                )  # 记录日志和发送成功信息
            else:
                self.log_and_send_error_message(roomid, trader_wxid, error_message)  # 记录日志和发送错误信息
        else:
            out_message = "-----XYBot-----\n转帐失败❌\n指令格式错误/在私聊转帐积分(仅可在群聊中转帐积分)❌"
            logger.info(f'[发送@信息]{out_message}| [@]{recv["sender"]}| [发送到] {recv["from"]}')
            self.bot.send_at_msg(recv["from"], out_message, [recv["sender"]])

    def get_error_message(self, target_wxid, trader_wxid, points_num: str):  # 获取错误信息
        if not target_wxid:
            return "\n-----XYBot-----\n转帐失败❌\n转帐人不存在(仅可转账群内成员)或⚠️转帐目标昵称重复⚠️"
        elif not points_num.isdigit():
            return "\n-----XYBot-----\n转帐失败❌\n转帐积分无效(必须为正整数!)"
        points_num = int(points_num)
        if not self.min_points <= points_num <= self.max_points:
            return f"\n-----XYBot-----\n转帐失败❌\n转帐积分无效(最大{self.max_points} 最小{self.min_points})"
        elif self.db.get_points(trader_wxid) < points_num:
            return f"\n-----XYBot-----\n积分不足！❌\n需要{points_num}点！"

    # 记录日志和发送成功信息
    def log_and_send_success_message(self, roomid, trader_wxid, target_wxid, points_num):
        trader_nick = self.bot.get_contact_profile(trader_wxid)["nickname"]  # 获取转账人昵称
        target_nick = self.bot.get_contact_profile(target_wxid)["nickname"]  # 获取转账目标昵称

        logger.success(
            f"[积分转帐]转帐人:{trader_wxid} {trader_nick}|目标:{target_wxid} {target_nick}|群:{roomid}|积分数:{points_num}"
        )
        trader_points, target_points = self.db.get_points(trader_wxid), self.db.get_points(target_wxid)
        out_message = f"\n-----XYBot-----\n转帐成功✅! 你现在有{trader_points}点积分 {target_nick}现在有{target_points}点积分"
        logger.info(f'[发送@信息]{out_message}| [@]{[trader_wxid, target_wxid]}| [发送到] {roomid}')
        self.bot.send_at_msg(roomid, out_message, [trader_wxid, target_wxid])

    def log_and_send_error_message(self, roomid, trader_wxid, error_message):  # 记录日志和发送错误信息
        logger.info(f'[发送@信息]{error_message}| [@]{trader_wxid}| [发送到] {roomid}')
        self.bot.send_at_msg(roomid, error_message, [trader_wxid])
