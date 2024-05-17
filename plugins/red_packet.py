import os
import random
import time

import schedule
import yaml
from captcha.image import ImageCaptcha
from loguru import logger

import pywxdll
from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface


class red_packet(PluginInterface):
    def __init__(self):
        config_path = "plugins/red_packet.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.max_point = config["max_point"]  # 最大积分
        self.min_point = config["min_point"]  # 最小积分
        self.max_packet = config["max_packet"]  # 最大红包数量
        self.max_time = config["max_time"]  # 红包超时时间

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config["ip"]  # 机器人ip
        self.port = main_config["port"]  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

        self.db = BotDatabase()  # 实例化机器人数据库类

        pic_cache_path = "resources/pic_cache"  # 检测是否有pic_cache文件夹
        if not os.path.exists(pic_cache_path):
            logger.info("检测到未创建pic_cache图片缓存文件夹")
            os.makedirs(pic_cache_path)
            logger.info("已创建pic_cach文件夹")

        self.red_packets = {}  # 红包列表

        # 定时任务 检查是否有超时红包
        schedule.every(self.max_time).seconds.do(self.check_left_red_packet)

    async def run(self, recv):
        if len(recv["content"]) == 3:  # 判断是否为红包指令
            self.send_red_packet(recv)
        elif len(recv["content"]) == 2:  # 判断是否为抢红包指令
            self.grab_red_packet(recv)
        else:  # 指令格式错误
            self.send_friend_or_group(
                recv, "-----XYBot-----\n❌命令格式错误！请查看菜单获取正确命令格式"
            )

    def send_red_packet(self, recv):
        # /红包 100 10

        if recv["id1"]:  # 判断是群还是私聊
            red_packet_sender = recv["id1"]
        else:
            red_packet_sender = recv["wxid"]

        # 判断是否有错误
        error = ""
        if not recv["id1"]:
            error = "-----XYBot-----\n❌红包只能在群里发！"
        elif not recv["content"][1].isdigit() or not recv["content"][2].isdigit():
            error = "-----XYBot-----\n❌指令格式错误！请查看菜单！"
        elif (
                int(recv["content"][1]) >= self.max_point
                or int(recv["content"][1]) <= self.min_point
        ):
            error = f"-----XYBot-----\n⚠️积分无效！最大{self.max_point}，最小{self.min_point}！"
        elif int(recv["content"][2]) >= self.max_packet:
            error = f"-----XYBot-----\n⚠️红包数量无效！最大{self.max_packet}！"

        # 判断是否有足够积分
        if not error:
            if self.db.get_points(red_packet_sender) < int(recv["content"][1]):
                error = "-----XYBot-----\n❌积分不足！"

        if not error:
            red_packet_points = int(recv["content"][1])  # 红包积分
            red_packet_amount = int(recv["content"][2])  # 红包数量
            red_packet_chatroom = recv["wxid"]  # 红包所在群聊

            red_packet_sender_nick = self.bot.get_chatroom_nickname(
                recv["wxid"], red_packet_sender
            )[
                "nick"
            ]  # 获取昵称
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
            out_message = f"-----XYBot-----\n{red_packet_sender_nick} 发送了一个红包！\n\n🧧红包金额：{red_packet_points}点积分\n🧧红包数量：{red_packet_amount}个\n\n🧧红包口令请见下图！\n\n快输入指令来抢红包！/抢红包 (口令)"

            # 发送信息
            self.bot.send_txt_msg(recv["wxid"], out_message)
            logger.info(
                f'[发送信息] (红包口令图片) {captcha_path} | [发送到] {recv["wxid"]}'
            )

            self.bot.send_pic_msg(recv["wxid"], captcha_path)


        else:
            self.send_friend_or_group(recv, error)  # 发送错误信息

    def grab_red_packet(self, recv):
        if recv["id1"]:  # 判断是群还是私聊
            red_packet_grabber = recv["id1"]
        else:
            red_packet_grabber = recv["wxid"]

        req_captcha = recv["content"][1]

        # 判断是否有错误
        error = ""
        if req_captcha not in self.red_packets.keys():
            error = "-----XYBot-----\n❌口令错误或无效！"
        elif not self.red_packets[req_captcha]["list"]:
            error = "-----XYBot-----\n⚠️红包已被抢完！"
        elif not recv["id1"]:
            error = "-----XYBot-----\n❌红包只能在群里抢！"
        elif red_packet_grabber in self.red_packets[req_captcha]["grabbed"]:
            error = "-----XYBot-----\n⚠️你已经抢过这个红包了！"
        elif self.red_packets[req_captcha]["sender"] == red_packet_grabber:
            error = "-----XYBot-----\n❌不能抢自己的红包！"

        if not error:
            try:  # 抢红包
                grabbed_points = self.red_packets[req_captcha][
                    "list"
                ].pop()  # 抢到的积分
                self.red_packets[req_captcha]["grabbed"].append(
                    red_packet_grabber
                )  # 把抢红包的人加入已抢列表
                red_packet_grabber_nick = self.bot.get_chatroom_nickname(
                    recv["wxid"], red_packet_grabber
                )[
                    "nick"
                ]  # 获取昵称

                self.db.add_points(red_packet_grabber, grabbed_points)  # 增加积分

                # 组建信息
                out_message = f"-----XYBot-----\n🧧恭喜 {red_packet_grabber_nick} 抢到了 {grabbed_points} 点积分！"
                self.send_friend_or_group(recv, out_message)

                # 判断是否抢完
                if not self.red_packets[req_captcha]["list"]:
                    self.red_packets.pop(req_captcha)

            except IndexError:
                error = "-----XYBot-----\n❌红包已被抢完！"
                self.send_friend_or_group(recv, error)

                return

        else:
            # 发送错误信息
            self.send_friend_or_group(recv, error)

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
            "v",
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
        path = f"resources/pic_cache/{chr_5}.jpg"
        captcha_image.save(path)

        return chr_5, path

    @staticmethod
    def split_integer(n, num_parts):
        # 生成 num_parts-1 个随机数
        random_numbers = []
        for _ in range(num_parts - 1):
            random_numbers.append(random.randint(1, n - num_parts + 1))
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

    def check_left_red_packet(self):  # 检查是否有超时红包
        logger.info("[计划任务]检查是否有超时的红包")
        for key in list(self.red_packets.keys()):
            if (
                    time.time() - self.red_packets[key]["time"] > self.max_time
            ):  # 判断是否超时
                red_packet_sender = self.red_packets[key]["sender"]  # 获取红包发送人
                red_packet_points_left_sum = sum(
                    self.red_packets[key]["list"]
                )  # 获取剩余积分
                red_packet_chatroom = self.red_packets[key][
                    "chatroom"
                ]  # 获取红包所在群聊
                red_packet_sender_nick = self.red_packets[key][
                    "sender_nick"
                ]  # 获取红包发送人昵称

                self.db.add_points(
                    red_packet_sender, red_packet_points_left_sum
                )  # 归还积分
                self.red_packets.pop(key)  # 删除红包
                logger.info("[红包]有红包超时，已归还积分！")  # 记录日志

                # 组建信息并发送
                out_message = f"-----XYBot-----\n🧧发现有红包 {key} 超时！已归还剩余 {red_packet_points_left_sum} 积分给 {red_packet_sender_nick}"
                self.bot.send_txt_msg(red_packet_chatroom, out_message)
                logger.info(f"[发送信息]{out_message}| [发送到] {red_packet_chatroom}")

    def send_friend_or_group(self, recv, out_message="null"):  # 发送信息
        if recv["id1"]:  # 判断是群还是私聊
            nickname = self.bot.get_chatroom_nickname(recv["wxid"], recv["id1"])["nick"]
            logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
            self.bot.send_at_msg(
                recv["wxid"], recv["id1"], nickname, "\n" + out_message
            )  # 发送

        else:
            logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
            self.bot.send_txt_msg(recv["wxid"], out_message)  # 发送
