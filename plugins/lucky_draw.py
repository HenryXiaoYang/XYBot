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

        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.ip = main_config['ip']
        self.port = main_config['port']
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api
        self.bot.start()  # 开启机器人

        self.db = database.BotDatabase()

    def run(self, recv):
        if recv['id1']:  # 用于判断是否为管理员
            target_wxid = recv['id1']  # 是群
        else:
            target_wxid = recv['wxid']  # 是私聊

        command = recv['content']
        draw_name = command[1]

        target_points = self.db.get_points(target_wxid)

        error = ''
        if len(command) != 2:
            error = '-----XYBot-----\n❌命令格式错误！请查看菜单获取正确命令格式'
        elif not draw_name in self.lucky_draw_probability.keys():
            error = '-----XYBot-----\n❌抽奖种类未知或者无效'
        elif draw_name in self.lucky_draw_probability.keys() and target_points < self.lucky_draw_probability[draw_name][
            'cost']:
            error = '-----XYBot-----\n❌积分不足！'

        if not error:
            draw_probability = self.lucky_draw_probability[draw_name]['probability']
            draw_cost = self.lucky_draw_probability[draw_name]['cost']

            self.db.add_points(target_wxid, -1 * draw_cost)

            random_num = random.uniform(0, 1)
            cumulative_probability = 0
            for probability, prize_dict in draw_probability.items():
                cumulative_probability += float(probability)
                if random_num <= cumulative_probability:
                    win_name = prize_dict['name']
                    win_points = prize_dict['points']

                    logger.info(
                        '[抽奖] {target_wxid}在{draw_name}抽奖中抽到了{win_name} 抽到了{win_points}点积分'.format(
                            target_wxid=target_wxid, draw_name=draw_name, win_name=win_name, win_points=win_points))
                    self.db.add_points(target_wxid, win_points)
                    out_message = '-----XYBot-----\n🥳恭喜你在 {draw_name}抽奖 中抽到了 {win_name}！✌️你抽到了 {win_points} 点积分！\n🙏🏻谢谢惠顾！\n\n🥳你在抽 {draw_name}抽奖 ，{draw_name}抽奖 需要{draw_cost}点积分💰，中奖概率如下❗️\n\n'.format(
                        draw_name=draw_name, draw_cost=draw_cost, win_name=win_name, win_points=win_points)

                    for probability, prize_info in draw_probability.items():
                        message = '🤑{prize_name}：概率为{probability}%，奖励为{prize_points}点积分\n'.format(
                            prize_name=prize_info['name'], probability=int(float(probability) * 100),
                            prize_points=prize_info['points'])
                        out_message += message
                    self.send_friend_or_group(recv, out_message)

                    break

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
