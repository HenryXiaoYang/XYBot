#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.
#
#  This program is licensed under the GNU General Public License v3.0.

import os
import random

import pywxdll
import yaml
from loguru import logger

import database
from plugin_interface import PluginInterface


class lucky_draw(PluginInterface):
    def __init__(self):
        config_path = os.path.abspath(__file__)[:-3] + '.yml'
        with open(config_path, 'r', encoding='utf-8') as f:  # 读取设置
            config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.lucky_draw_probability = config['lucky_draw_probability']
        self.max_draw = config['max_draw']

        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.ip = main_config['ip']
        self.port = main_config['port']
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

        self.db = database.BotDatabase()

    def run(self, recv):
        global draw_count, draw_name

        # -----初始化与消息格式监测-----

        if recv['id1']:  # 用于判断是否为管理员
            target_wxid = recv['id1']  # 是群
        else:
            target_wxid = recv['wxid']  # 是私聊

        command = recv['content']

        target_points = self.db.get_points(target_wxid)

        error = ''

        if len(command) == 2:
            draw_name = command[1]
            draw_count = 1

            if draw_name not in self.lucky_draw_probability.keys():
                error = '-----XYBot-----\n❌抽奖种类未知或者无效'
            elif draw_name in self.lucky_draw_probability.keys() and target_points < \
                    self.lucky_draw_probability[draw_name][
                        'cost']:
                error = '-----XYBot-----\n❌积分不足！'

        elif len(command) == 3:
            draw_name = command[1]
            draw_count = int(command[2])

            if draw_name not in self.lucky_draw_probability.keys():
                error = '-----XYBot-----\n❌抽奖种类未知或者无效'
            elif draw_name in self.lucky_draw_probability.keys() and target_points < \
                    self.lucky_draw_probability[draw_name][
                        'cost'] * draw_count:
                error = '-----XYBot-----\n❌积分不足！'
        else:
            error = '-----XYBot-----\n❌命令格式错误！请查看菜单获取正确命令格式'

        if not error:

            # -----抽奖核心部分-----

            draw_probability = self.lucky_draw_probability[draw_name]['probability']
            draw_cost = self.lucky_draw_probability[draw_name]['cost'] * draw_count

            wins = []

            self.db.add_points(target_wxid, -1 * draw_cost)

            # 保底抽奖
            min_guaranteed = draw_count // 10
            for _ in range(min_guaranteed):
                random_num = random.uniform(0, 0.4)
                cumulative_probability = 0
                for probability, prize_dict in draw_probability.items():
                    cumulative_probability += float(probability)
                    if random_num <= cumulative_probability:
                        win_name = prize_dict['name']
                        win_points = prize_dict['points']
                        win_symbol = prize_dict['symbol']

                        wins.append((win_name, win_points, win_symbol))
                        break

            # 正常抽奖
            for _ in range(draw_count - min_guaranteed):
                random_num = random.uniform(0, 1)
                cumulative_probability = 0
                for probability, prize_dict in draw_probability.items():
                    cumulative_probability += float(probability)
                    if random_num <= cumulative_probability:
                        win_name = prize_dict['name']
                        win_points = prize_dict['points']
                        win_symbol = prize_dict['symbol']

                        wins.append((win_name, win_points, win_symbol))
                        break

            # -----消息组建-----

            total_win_points = 0
            for win_name, win_points, win_symbol in wins:
                total_win_points += win_points

            self.db.add_points(target_wxid, total_win_points)
            logger.info(
                f'[抽奖] wxid: {target_wxid} | 抽奖名: {draw_name} | 次数: {draw_count} | 赢取积分: {total_win_points}')

            message = self.make_message(wins, draw_name, draw_count, total_win_points, draw_cost)

            self.send_friend_or_group(recv, message)

        else:
            self.send_friend_or_group(recv, error)

    def send_friend_or_group(self, recv, out_message='null'):
        if recv['id1']:  # 判断是群还是私聊
            nickname = self.bot.get_chatroom_nickname(recv['wxid'], recv['id1'])['nick']
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, '\n' + out_message)  # 发送
        else:
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)  # 发送

    @staticmethod
    def make_message(wins, draw_name, draw_count, total_win_points, draw_cost):
        name_max_len = 0
        for win_name, win_points, win_symbol in wins:
            if len(win_name) > name_max_len:
                name_max_len = len(win_name)

        begin_message = f"----XYBot抽奖----\n🥳恭喜你在 {draw_count}次 {draw_name}抽奖 中抽到了：\n\n"
        lines = []
        for _ in range(name_max_len + 2):
            lines.append('')

        begin_line = 0

        one_line_length = 0

        for win_name, win_points, win_symbol in wins:
            if one_line_length >= 10:
                begin_line += name_max_len + 2
                for _ in range(name_max_len + 2):
                    lines.append('')
                one_line_length = 0

            lines[begin_line] += win_symbol
            for i in range(begin_line + 1, begin_line + name_max_len + 1):
                if i % (name_max_len + 2) <= len(win_name):
                    lines[i] += "\u2004" + win_name[i % (name_max_len + 2) - 1]
                else:
                    lines[i] += win_symbol
            lines[begin_line + name_max_len + 1] += win_symbol

            one_line_length += 1

        message = ''
        message += begin_message
        for line in lines:
            message += line + '\n'

        message += f"\n\n🎉总计赢取积分: {total_win_points}🎉\n🎉共计消耗积分：{draw_cost}🎉\n\n概率请自行查询菜单⚙️"

        return message
