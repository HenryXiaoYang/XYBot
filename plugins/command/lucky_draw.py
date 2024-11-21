#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import random
import re

import yaml
from loguru import logger
from wcferry import client

from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface
from wcferry_helper import XYBotWxMsg


class lucky_draw(PluginInterface):
    def __init__(self):
        config_path = "plugins/command/lucky_draw.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.command_format_menu = config["command_format_menu"]  # 命令格式

        self.lucky_draw_probability = config["lucky_draw_probability"]  # 抽奖概率
        self.max_draw = config["max_draw"]  # 连抽最大数量
        self.draw_per_guarantee = config[
            "draw_per_guarantee"
        ]  # 保底抽奖次数 每个保底需要x抽
        self.guaranteed_max_probability = config["guaranteed_max_probability"]

        self.db = BotDatabase()  # 实例化数据库类

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        recv.content = re.split(" |\u2005", recv.content)  # 拆分消息

        global _draw_count, _draw_name  # 全局变量防止出错

        # -----初始化与消息格式监测-----
        target_wxid = recv.sender  # 获取发送者wxid

        command = recv.content  # 指令

        target_points = self.db.get_points(target_wxid)  # 获取目标积分

        error = ""

        if len(command) == 2:  # 判断指令格式
            _draw_name = command[1]  # 抽奖名
            _draw_count = 1  # 抽奖次数，单抽设为1

            if (
                    _draw_name not in self.lucky_draw_probability.keys()
            ):  # 判断抽奖是否有效，积分是否够
                error = "-----XYBot-----\n❌抽奖种类未知或者无效"
            elif (
                    _draw_name in self.lucky_draw_probability.keys()
                    and target_points < self.lucky_draw_probability[_draw_name]["cost"]
            ):
                error = "-----XYBot-----\n❌积分不足！"

        elif len(command) == 3 and command[2].isdigit():
            _draw_name = command[1]
            _draw_count = int(command[2])

            if (
                    _draw_name not in self.lucky_draw_probability.keys()
            ):  # 判断抽奖是否有效，积分是否够，连抽要乘次数
                error = "-----XYBot-----\n❌抽奖种类未知或者无效"
            elif (
                    _draw_name in self.lucky_draw_probability.keys()
                    and target_points
                    < self.lucky_draw_probability[_draw_name]["cost"] * _draw_count
            ):
                error = "-----XYBot-----\n❌积分不足！"
        else:  # 指令格式错误
            error = f"-----XYBot-----\n❌命令格式错误！\n\n{self.command_format_menu}"

        if not error:

            # -----抽奖核心部分-----

            draw_probability = self.lucky_draw_probability[_draw_name][
                "probability"
            ]  # 从设置获取抽奖名概率
            draw_cost = (
                    self.lucky_draw_probability[_draw_name]["cost"] * _draw_count
            )  # 从设置获取抽奖消耗积分

            wins = []  # 赢取列表

            self.db.add_points(target_wxid, -1 * draw_cost)  # 扣取积分

            # 保底抽奖
            min_guaranteed = _draw_count // self.draw_per_guarantee  # 保底抽奖次数
            for _ in range(min_guaranteed):  # 先把保底抽了
                random_num = random.uniform(0, self.guaranteed_max_probability)
                cumulative_probability = 0
                for probability, prize_dict in draw_probability.items():
                    cumulative_probability += float(probability)
                    if random_num <= cumulative_probability:
                        win_name = prize_dict["name"]
                        win_points = prize_dict["points"]
                        win_symbol = prize_dict["symbol"]

                        wins.append(
                            (win_name, win_points, win_symbol)
                        )  # 把结果加入赢取列表
                        break

            # 正常抽奖
            for _ in range(_draw_count - min_guaranteed):  # 把剩下的抽了
                random_num = random.uniform(0, 1)
                cumulative_probability = 0
                for probability, prize_dict in draw_probability.items():
                    cumulative_probability += float(probability)
                    if random_num <= cumulative_probability:
                        win_name = prize_dict["name"]
                        win_points = prize_dict["points"]
                        win_symbol = prize_dict["symbol"]

                        wins.append(
                            (win_name, win_points, win_symbol)
                        )  # 把结果加入赢取列表
                        break

            # -----消息组建-----

            total_win_points = 0
            for win_name, win_points, win_symbol in wins:  # 统计赢取的积分
                total_win_points += win_points

            self.db.add_points(target_wxid, total_win_points)  # 把赢取的积分加入数据库
            logger.info(
                f"[抽奖] wxid: {target_wxid} | 抽奖名: {_draw_name} | 次数: {_draw_count} | 赢取积分: {total_win_points}"
            )

            message = self.make_message(
                wins, _draw_name, _draw_count, total_win_points, draw_cost
            )  # 组建信息

            await self.send_friend_or_group(bot, recv, message)  # 发送
            bot.send_pat_msg(recv.roomid, target_wxid)  # 发送拍一拍消息

        else:
            await self.send_friend_or_group(bot, recv, error)  # 发送错误

    async def send_friend_or_group(self, bot: client.Wcf, recv: XYBotWxMsg, out_message="null"):
        if recv.from_group():  # 判断是群还是私聊
            out_message = f"@{self.db.get_nickname(recv.sender)}\n{out_message}"
            logger.info(f'[发送@信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid, recv.sender)  # 发送@信息
        else:
            logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid)  # 发送

    @staticmethod
    def make_message(
            wins, _draw_name, _draw_count, total_win_points, draw_cost
    ):  # 组建信息
        name_max_len = 0
        for win_name, win_points, win_symbol in wins:
            if len(win_name) > name_max_len:
                name_max_len = len(win_name)

        begin_message = f"----XYBot抽奖----\n🥳恭喜你在 {_draw_count}次 {_draw_name}抽奖 中抽到了：\n\n"
        lines = []
        for _ in range(name_max_len + 2):
            lines.append("")

        begin_line = 0

        one_line_length = 0

        for win_name, win_points, win_symbol in wins:
            if one_line_length >= 10:  # 每行10个结果，以免在微信上格式错误
                begin_line += name_max_len + 2
                for _ in range(name_max_len + 2):
                    lines.append("")  # 占个位
                one_line_length = 0

            lines[begin_line] += win_symbol
            for i in range(begin_line + 1, begin_line + name_max_len + 1):
                if i % (name_max_len + 2) <= len(win_name):
                    lines[i] += (
                            "\u2004" + win_name[i % (name_max_len + 2) - 1]
                    )  # \u2004 这个空格最好 试过了很多种空格
                else:
                    lines[i] += win_symbol
            lines[begin_line + name_max_len + 1] += win_symbol

            one_line_length += 1

        message = begin_message
        for line in lines:
            message += line + "\n"

        message += f"\n\n🎉总计赢取积分: {total_win_points}🎉\n🎉共计消耗积分：{draw_cost}🎉\n\n概率请自行查询菜单⚙️"

        return message
