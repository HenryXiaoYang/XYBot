#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import yaml
from loguru import logger
from wcferry import client

from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface
from wcferry_helper import XYBotWxMsg


class points_leaderboard(PluginInterface):
    def __init__(self):
        config_path = "plugins/command/points_leaderboard.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.leaderboard_top_number = config[
            "leaderboard_top_number"
        ]  # 显示积分榜前x名人

        self.db = BotDatabase()  # 实例化数据库类

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        recv.content = recv.content.split(" |\u2005")  # 拆分消息

        data = self.db.get_highest_points(
            self.leaderboard_top_number
        )  # 从数据库获取前x名积分数
        out_message = "-----XYBot积分排行榜-----"  # 创建积分
        rank = 1
        for i in data:  # 从数据库获取的数据中for循环
            nickname = self.db.get_nickname(i[0])  # 获取昵称
            if not nickname:
                nickname = i[0]

            out_message += f"\n{rank}. {nickname} {i[1]}分 👍"
            rank += 1
            # 组建积分榜信息

        out_message += "\n\n现在无法直接获取到昵称，需要发过消息的用户才能获取到昵称\n如果没发过只能显示wxid了"

        logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
        bot.send_text(out_message, recv.roomid)  # 发送
