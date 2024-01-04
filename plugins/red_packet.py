#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.
#
#  This program is licensed under the GNU General Public License v3.0.

import os
import random
import time

import pywxdll
import yaml
from captcha.image import ImageCaptcha
from loguru import logger

from database import BotDatabase
from plugin_interface import PluginInterface


class red_packet(PluginInterface):
    def __init__(self):
        config_path = os.path.abspath(__file__)[:-3] + '.yml'
        with open(config_path, 'r', encoding='utf-8') as f:  # 读取设置
            config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.max_point = config['max_point']
        self.min_point = config['min_point']
        self.max_packet = config['max_packet']
        self.max_time = config['max_time']

        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.ip = main_config['ip']
        self.port = main_config['port']
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

        self.db = BotDatabase()  # 放在init会不在一个线程上，数据库会报错

        self.red_packets = {}

    def run(self, recv):
        self.check_left_red_packet()

        if len(recv['content']) == 3:
            self.send_red_packet(recv)
        elif len(recv['content']) == 2:
            self.grab_red_packet(recv)
        else:
            self.send_friend_or_group(recv, '-----XYBot-----\n❌命令格式错误！请查看菜单获取正确命令格式')

    def send_red_packet(self, recv):
        # /红包 100 10

        if recv['id1']:
            red_packet_sender = recv['id1']
        else:
            red_packet_sender = recv['wxid']

        error = ''

        if not recv['id1']:
            error = '-----XYBot-----\n❌红包只能在群里发！'
        elif not recv['content'][1].isdigit() or not recv['content'][2].isdigit():
            error = '-----XYBot-----\n❌指令格式错误！请查看菜单！'
        elif int(recv['content'][1]) > self.max_point or int(recv['content'][1]) < self.min_point:
            error = '-----XYBot-----\n⚠️积分无效！最大{max_points}，最小{min_points}！'.format(max_points=self.max_point,
                                                                                            min_points=self.min_point)
        elif int(recv['content'][2]) >= self.max_packet:
            error = '-----XYBot-----\n⚠️红包数量无效！最大{max_packet}！'.format(max_packet=self.max_packet)

        if not error:
            if self.db.get_points(red_packet_sender) < int(recv['content'][1]):
                error = '-----XYBot-----\n❌积分不足！'

        if not error:
            red_packet_points = int(recv['content'][1])
            red_packet_amount = int(recv['content'][2])

            red_packet_sender_nick = self.bot.get_chatroom_nickname(recv['wxid'], red_packet_sender)['nick']
            red_packet_points_list = self.split_integer(red_packet_points, red_packet_amount)

            chr_5, captcha_path = self.generate_captcha()
            captcha_path = os.path.abspath(captcha_path)

            red_packet = {'points': red_packet_points, 'amount': red_packet_amount, 'sender': red_packet_sender,
                          'list': red_packet_points_list, 'grabbed': [], 'time': time.time()}
            self.red_packets[chr_5] = red_packet
            self.db.add_points(red_packet_sender, red_packet_points * -1)

            out_message = '-----XYBot-----\n{red_packet_sender_nick} 发送了一个红包！\n\n🧧红包金额：{red_packet_points}点积分\n🧧红包数量：{red_packet_amount}个\n\n🧧红包口令请见下图！\n\n快输入指令来抢红包！/抢红包 (口令)'.format(
                red_packet_sender_nick=red_packet_sender_nick, red_packet_points=red_packet_points,
                red_packet_amount=red_packet_amount)

            self.bot.send_txt_msg(recv['wxid'], out_message)
            logger.info(
                '[发送信息] (红包验证码图片) {path} | [发送到] {wxid}'.format(path=captcha_path,
                                                                              out_message=out_message,
                                                                              wxid=recv['wxid']))
            self.bot.send_pic_msg(recv['wxid'], captcha_path)

        else:
            self.send_friend_or_group(recv, error)

    def grab_red_packet(self, recv):
        if recv['id1']:
            red_packet_grabber = recv['id1']
        else:
            red_packet_grabber = recv['wxid']

        req_captcha = recv['content'][1]

        error = ''
        if not req_captcha in self.red_packets.keys():
            error = '-----XYBot-----\n❌口令错误或无效！'
        elif not self.red_packets[req_captcha]['list']:
            error = '-----XYBot-----\n⚠️红包已被抢完！'
        elif not recv['id1']:
            error = '-----XYBot-----\n❌红包只能在群里抢！'
        elif red_packet_grabber in self.red_packets[req_captcha]['grabbed']:
            error = '-----XYBot-----\n⚠️你已经抢过这个红包了！'
        elif self.red_packets[req_captcha]['sender'] == red_packet_grabber:
            error = '-----XYBot-----\n❌不能抢自己的红包！'

        if not error:
            try:
                grabbed_points = self.red_packets[req_captcha]['list'].pop()
                self.red_packets[req_captcha]['grabbed'].append(red_packet_grabber)
                red_packet_grabber_nick = self.bot.get_chatroom_nickname(recv['wxid'], red_packet_grabber)['nick']

                self.db.add_points(red_packet_grabber, grabbed_points)
                out_message = '-----XYBot-----\n🧧恭喜 {red_packet_grabber_nick} 抢到了 {grabbed_points} 点积分！'.format(
                    red_packet_grabber_nick=red_packet_grabber_nick, grabbed_points=grabbed_points)
                self.send_friend_or_group(recv, out_message)

                if not self.red_packets[req_captcha]['list']:
                    self.red_packets.pop(req_captcha)

            except IndexError:
                error = '-----XYBot-----\n❌红包已被抢完！'
                self.send_friend_or_group(recv, error)
                return

        else:
            self.send_friend_or_group(recv, error)
            return

    def generate_captcha(self):
        chr_all = ['a', 'b', 'c', 'd', 'f', 'g', 'h', 'k', 'm', 'n', 'p', 'q', 'r', 't', 'v', 'w', 'x', 'y',
                   '2', '3', '4', '6', '7', '8', '9']
        chr_5 = ''.join(random.sample(chr_all, 5))
        captcha_image = ImageCaptcha().generate_image(chr_5)
        path = 'resources/pic_cache/{captcha}.jpg'.format(captcha=chr_5)
        captcha_image.save(path)

        return chr_5, path

    def split_integer(self, n, num_parts):
        # 生成 num_parts-1 个随机数
        random_numbers = []
        for _ in range(num_parts - 1):
            random_numbers.append(random.randint(1, n))
        random_numbers.sort()

        # 计算每份的数量
        parts = []
        prev = 0
        for num in random_numbers:
            parts.append(num - prev)
            prev = num
        parts.append(n - prev)
        random.shuffle(parts)
        return parts

    def check_left_red_packet(self):
        for key in self.red_packets.keys():
            if time.time() - self.red_packets[key]['time'] > self.max_time:
                red_packet_sender = self.red_packets[key]['sender']
                red_packet_points_left_sum = sum(self.red_packets[key]['list'])
                self.db.add_points(red_packet_sender, red_packet_points_left_sum)
                self.red_packets.pop(key)
                logger.info('[红包]有红包超时，已归还积分！')

    def send_friend_or_group(self, recv, out_message='null'):
        if recv['id1']:  # 判断是群还是私聊
            nickname = self.bot.get_chatroom_nickname(recv['wxid'], recv['id1'])['nick']
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, '\n' + out_message)  # 发送
        else:
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)  # 发送
