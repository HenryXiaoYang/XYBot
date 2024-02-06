import random

import pywxdll
import yaml
from loguru import logger

import database
from plugin_interface import PluginInterface


class lucky_draw(PluginInterface):
    def __init__(self):
        config_path = 'plugins/lucky_draw.yml'
        with open(config_path, 'r', encoding='utf-8') as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.lucky_draw_probability = config['lucky_draw_probability']  # 抽奖概率
        self.max_draw = config['max_draw']  # 连抽最大数量
        self.draw_per_guarantee = config['draw_per_guarantee']  # 保底抽奖次数 每个保底需要x抽
        self.guaranteed_max_probability = config['guaranteed_max_probability']

        main_config_path = 'main_config.yml'
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config['ip']  # 机器人ip
        self.port = main_config['port']  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

        self.db = database.BotDatabase()  # 实例化数据库类

    async def run(self, recv):
        global draw_count, draw_name  # 全局变量防止出错

        # -----初始化与消息格式监测-----

        if recv['id1']:  # 用于判断是否为管理员
            target_wxid = recv['id1']  # 是群
        else:
            target_wxid = recv['wxid']  # 是私聊

        command = recv['content']  # 指令

        target_points = self.db.get_points(target_wxid)  # 获取目标积分

        error = ''

        if len(command) == 2:  # 判断指令格式
            draw_name = command[1]  # 抽奖名
            draw_count = 1  # 抽奖次数，单抽设为1

            if draw_name not in self.lucky_draw_probability.keys():  # 判断抽奖是否有效，积分是否够
                error = '-----XYBot-----\n❌抽奖种类未知或者无效'
            elif draw_name in self.lucky_draw_probability.keys() and target_points < \
                    self.lucky_draw_probability[draw_name][
                        'cost']:
                error = '-----XYBot-----\n❌积分不足！'

        elif len(command) == 3 and command[2].isdigit():
            draw_name = command[1]
            draw_count = int(command[2])

            if draw_name not in self.lucky_draw_probability.keys():  # 判断抽奖是否有效，积分是否够，连抽要乘次数
                error = '-----XYBot-----\n❌抽奖种类未知或者无效'
            elif draw_name in self.lucky_draw_probability.keys() and target_points < \
                    self.lucky_draw_probability[draw_name][
                        'cost'] * draw_count:
                error = '-----XYBot-----\n❌积分不足！'
        else:  # 指令格式错误
            error = '-----XYBot-----\n❌命令格式错误！请查看菜单获取正确命令格式'

        if not error:

            # -----抽奖核心部分-----

            draw_probability = self.lucky_draw_probability[draw_name]['probability']  # 从设置获取抽奖名概率
            draw_cost = self.lucky_draw_probability[draw_name]['cost'] * draw_count  # 从设置获取抽奖消耗积分

            wins = []  # 赢取列表

            self.db.add_points(target_wxid, -1 * draw_cost)  # 扣取积分

            # 保底抽奖
            min_guaranteed = draw_count // self.draw_per_guarantee  # 保底抽奖次数
            for _ in range(min_guaranteed):  # 先把保底抽了
                random_num = random.uniform(0, self.guaranteed_max_probability)
                cumulative_probability = 0
                for probability, prize_dict in draw_probability.items():
                    cumulative_probability += float(probability)
                    if random_num <= cumulative_probability:
                        win_name = prize_dict['name']
                        win_points = prize_dict['points']
                        win_symbol = prize_dict['symbol']

                        wins.append((win_name, win_points, win_symbol))  # 把结果加入赢取列表
                        break

            # 正常抽奖
            for _ in range(draw_count - min_guaranteed):  # 把剩下的抽了
                random_num = random.uniform(0, 1)
                cumulative_probability = 0
                for probability, prize_dict in draw_probability.items():
                    cumulative_probability += float(probability)
                    if random_num <= cumulative_probability:
                        win_name = prize_dict['name']
                        win_points = prize_dict['points']
                        win_symbol = prize_dict['symbol']

                        wins.append((win_name, win_points, win_symbol))  # 把结果加入赢取列表
                        break

            # -----消息组建-----

            total_win_points = 0
            for win_name, win_points, win_symbol in wins:  # 统计赢取的积分
                total_win_points += win_points

            self.db.add_points(target_wxid, total_win_points)  # 把赢取的积分加入数据库
            logger.info(
                f'[抽奖] wxid: {target_wxid} | 抽奖名: {draw_name} | 次数: {draw_count} | 赢取积分: {total_win_points}')

            message = self.make_message(wins, draw_name, draw_count, total_win_points, draw_cost)  # 组建信息

            self.send_friend_or_group(recv, message)  # 发送

        else:
            self.send_friend_or_group(recv, error)  # 发送错误

    def send_friend_or_group(self, recv, out_message='null'):
        if recv['id1']:  # 判断是群还是私聊
            nickname = self.bot.get_chatroom_nickname(recv['wxid'], recv['id1'])['nick']
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, '\n' + out_message)  # 发送
        else:
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)  # 发送

    @staticmethod
    def make_message(wins, draw_name, draw_count, total_win_points, draw_cost):  # 组建信息
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
            if one_line_length >= 10:  # 每行10个结果，以免在微信上格式错误
                begin_line += name_max_len + 2
                for _ in range(name_max_len + 2):
                    lines.append('')  # 占个位
                one_line_length = 0

            lines[begin_line] += win_symbol
            for i in range(begin_line + 1, begin_line + name_max_len + 1):
                if i % (name_max_len + 2) <= len(win_name):
                    lines[i] += "\u2004" + win_name[i % (name_max_len + 2) - 1]  # \u2004 这个空格最好 试过了很多种空格
                else:
                    lines[i] += win_symbol
            lines[begin_line + name_max_len + 1] += win_symbol

            one_line_length += 1

        message = begin_message
        for line in lines:
            message += line + '\n'

        message += f"\n\n🎉总计赢取积分: {total_win_points}🎉\n🎉共计消耗积分：{draw_cost}🎉\n\n概率请自行查询菜单⚙️"

        return message
