#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import os
import random
import re
import time

import yaml
from captcha.image import ImageCaptcha
from loguru import logger
from wcferry import client

from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface
from wcferry_helper import XYBotWxMsg


class red_packet(PluginInterface):
    def __init__(self):
        config_path = "plugins/command/red_packet.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.command_format_menu = config["command_format_menu"]  # 指令格式

        self.max_point = config["max_point"]  # 最大积分
        self.min_point = config["min_point"]  # 最小积分
        self.max_packet = config["max_packet"]  # 最大红包数量
        self.max_time = config["max_time"]  # 红包超时时间

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.command_prefix = main_config["command_prefix"]

        self.db = BotDatabase()  # 实例化机器人数据库类

        cache_path = "resources/cache"  # 检测是否有cache文件夹
        if not os.path.exists(cache_path):
            logger.info("检测到未创建cache缓存文件夹")
            os.makedirs(cache_path)
            logger.info("已创建cache文件夹")

        self.red_packets = {}  # 红包列表

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        recv.content = re.split(" |\u2005", recv.content)  # 拆分消息

        if len(recv.content) == 3:  # 判断是否为红包指令
            await self.send_red_packet(bot, recv)
        elif len(recv.content) == 2:  # 判断是否为抢红包指令
            await self.grab_red_packet(bot, recv)
        else:  # 指令格式错误
            await self.send_friend_or_group(bot, recv, f"-----XYBot-----\n❌命令格式错误！{self.command_format_menu}")

    async def send_red_packet(self, bot: client.Wcf, recv: XYBotWxMsg):
        red_packet_sender = recv.sender

        # 判断是否有错误
        error = ""
        if not recv.from_group():
            error = "-----XYBot-----\n❌红包只能在群里发！"
        elif not recv.content[1].isdigit() or not recv.content[2].isdigit():
            error = "-----XYBot-----\n❌指令格式错误！请查看菜单！"
        elif int(recv.content[1]) > self.max_point or int(recv.content[1]) < self.min_point:
            error = f"-----XYBot-----\n⚠️积分无效！最大{self.max_point}，最小{self.min_point}！"
        elif int(recv.content[2]) > self.max_packet:
            error = f"-----XYBot-----\n⚠️红包数量无效！最大{self.max_packet}！"
        elif int(recv.content[2]) > int(recv.content[1]):
            error = "-----XYBot-----\n❌红包数量不能大于红包积分！"

        # 判断是否有足够积分
        if not error:
            if self.db.get_points(red_packet_sender) < int(recv.content[1]):
                error = "-----XYBot-----\n❌积分不足！"

        if not error:
            red_packet_points = int(recv.content[1])  # 红包积分
            red_packet_amount = int(recv.content[2])  # 红包数量
            red_packet_chatroom = recv.roomid  # 红包所在群聊

            red_packet_sender_nick = self.db.get_nickname(red_packet_sender)  # 获取昵称
            if not red_packet_sender_nick:
                red_packet_sender_nick = red_packet_sender

            red_packet_points_list = self.split_integer(
                red_packet_points, red_packet_amount
            )  # 随机分红包积分

            chr_5, captcha_path = self.generate_captcha()  # 生成口令
            captcha_path = os.path.abspath(captcha_path)  # 获取口令路径

            new_red_packet = {
                "points": red_packet_points,
                "amount": red_packet_amount,
                "sender": red_packet_sender,
                "list": red_packet_points_list,
                "grabbed": [],
                "time": time.time(),
                "chatroom": red_packet_chatroom,
                "sender_nick": red_packet_sender_nick,
            }  # 红包信息

            self.red_packets[chr_5] = new_red_packet  # 把红包放入红包列表
            self.db.add_points(red_packet_sender, red_packet_points * -1)  # 扣除积分

            # 组建信息
            out_message = f"-----XYBot-----\n{red_packet_sender_nick} 发送了一个红包！\n\n🧧红包金额：{red_packet_points}点积分\n🧧红包数量：{red_packet_amount}个\n\n🧧红包口令请见下图！\n\n快输入指令来抢红包！\n指令：{self.command_prefix}抢红包 口令"

            # 发送信息
            bot.send_text(out_message, recv.roomid)
            logger.info(f'[发送信息] (红包口令图片) {captcha_path} | [发送到] {recv.roomid}')

            bot.send_image(captcha_path, recv.roomid)


        else:
            await self.send_friend_or_group(bot, recv, error)  # 发送错误信息

    async def grab_red_packet(self, bot: client.Wcf, recv: XYBotWxMsg):
        red_packet_grabber = recv.sender

        req_captcha = recv.content[1]

        # 判断是否有错误
        error = ""
        if req_captcha not in self.red_packets.keys():
            error = "-----XYBot-----\n❌口令错误或无效！"
        elif not self.red_packets[req_captcha]["list"]:
            error = "-----XYBot-----\n⚠️红包已被抢完！"
        elif not recv.from_group():
            error = "-----XYBot-----\n❌红包只能在群里抢！"
        elif red_packet_grabber in self.red_packets[req_captcha]["grabbed"]:
            error = "-----XYBot-----\n⚠️你已经抢过这个红包了！"
        elif self.red_packets[req_captcha].sender == red_packet_grabber:
            error = "-----XYBot-----\n❌不能抢自己的红包！"

        if not error:
            try:  # 抢红包
                grabbed_points = self.red_packets[req_captcha][
                    "list"
                ].pop()  # 抢到的积分
                self.red_packets[req_captcha]["grabbed"].append(
                    red_packet_grabber
                )  # 把抢红包的人加入已抢列表

                red_packet_grabber_nick = self.db.get_nickname(red_packet_grabber)  # 获取昵称
                if not red_packet_grabber_nick:
                    red_packet_grabber_nick = red_packet_grabber

                self.db.add_points(red_packet_grabber, grabbed_points)  # 增加积分

                # 组建信息
                out_message = f"-----XYBot-----\n🧧恭喜 {red_packet_grabber_nick} 抢到了 {grabbed_points} 点积分！"
                await self.send_friend_or_group(bot, recv, out_message)

                # 判断是否抢完
                if not self.red_packets[req_captcha]["list"]:
                    self.red_packets.pop(req_captcha)

            except IndexError:
                error = "-----XYBot-----\n❌红包已被抢完！"
                await self.send_friend_or_group(bot, recv, error)

                return

        else:
            # 发送错误信息
            await self.send_friend_or_group(bot, recv, error)

            return

    @staticmethod
    def generate_captcha():  # 生成口令
        chr_all = [
            "a",
            "b",
            "d",
            "f",
            "g",
            "h",
            "k",
            "m",
            "n",
            "p",
            "q",
            "t",
            "w",
            "x",
            "y",
            "2",
            "3",
            "4",
            "6",
            "7",
            "8",
            "9",
        ]
        chr_5 = "".join(random.sample(chr_all, 5))
        captcha_image = ImageCaptcha().generate_image(chr_5)
        path = f"resources/cache/{chr_5}.jpg"
        captcha_image.save(path)

        return chr_5, path

    @staticmethod
    def split_integer(num, count):
        # 初始化每个数为1
        result = [1] * count
        remaining = num - count

        # 随机分配剩余的部分
        while remaining > 0:
            index = random.randint(0, count - 1)
            result[index] += 1
            remaining -= 1

        return result

    async def expired_red_packets_check(self, bot: client.Wcf):  # 检查是否有超时红包
        logger.info("[计划任务]检查是否有超时的红包")
        for key in list(self.red_packets.keys()):
            if time.time() - self.red_packets[key]["time"] > self.max_time:  # 判断是否超时

                red_packet_sender = self.red_packets[key].sender  # 获取红包发送人
                red_packet_points_left_sum = sum(self.red_packets[key]["list"])  # 获取剩余积分
                red_packet_chatroom = self.red_packets[key]["chatroom"]  # 获取红包所在群聊
                red_packet_sender_nick = self.red_packets[key]["sender_nick"]  # 获取红包发送人昵称

                self.db.add_points(red_packet_sender, red_packet_points_left_sum)  # 归还积分
                self.red_packets.pop(key)  # 删除红包
                logger.info("[红包]有红包超时，已归还积分！")  # 记录日志

                # 组建信息并发送
                out_message = f"-----XYBot-----\n🧧发现有红包 {key} 超时！已归还剩余 {red_packet_points_left_sum} 积分给 {red_packet_sender_nick}"
                bot.send_text(out_message, red_packet_chatroom)
                logger.info(f"[发送信息]{out_message}| [发送到] {red_packet_chatroom}")

    async def send_friend_or_group(self, bot: client.Wcf, recv: XYBotWxMsg, out_message="null"):
        if recv.from_group():  # 判断是群还是私聊
            out_message = f"@{self.db.get_nickname(recv.sender)}\n{out_message}"
            logger.info(f'[发送@信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid, recv.sender)  # 发送@信息
        else:
            logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid)  # 发送
