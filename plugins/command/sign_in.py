#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import random
from datetime import datetime
from datetime import timedelta

import pytz
import yaml
from loguru import logger

import pywxdll
from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface


class sign_in(PluginInterface):
    def __init__(self):
        config_path = "plugins/command/sign_in.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.min_points = config["min_points"]  # 最小积分
        self.max_points = config["max_points"]  # 最大积分

        self.min_lucky_star = config["min_lucky_star"]  # 最小幸运星数
        self.max_lucky_star = config["max_lucky_star"]  # 最大幸运星数
        self.lucky_star_message = config["lucky_star_message"]

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config["ip"]  # 机器人ip
        self.port = main_config["port"]  # 机器人端口
        self.timezone = main_config["timezone"]  # 时区

        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

        self.db = BotDatabase()

    async def run(self, recv):
        signin_points = random.randint(self.min_points, self.max_points)  # 随机3-20积分

        sign_wxid = recv["sender"]

        signstat = str(self.db.get_stat(sign_wxid))  # 从数据库获取签到状态

        if self.signstat_check(signstat):  # 如果今天未签到
            self.db.add_points(sign_wxid, signin_points)  # 在数据库加积分
            now_datetime = datetime.now(tz=pytz.timezone(self.timezone)).strftime("%Y%m%d")  # 获取现在格式化后时间
            self.db.set_stat(sign_wxid, now_datetime)  # 设置签到状态为现在格式化后时间

            # 运势
            lucky_num = random.randint(self.min_lucky_star, self.max_lucky_star)
            lucky_star = "⭐️" * lucky_num
            lucky_star_message = f"你的运势：{lucky_star}\n{self.lucky_star_message.get(lucky_num)}"

            out_message = f"\n-----XYBot-----\n签到成功！你领到了{signin_points}个积分！✅\n\n{lucky_star_message}"  # 创建发送信息
            logger.info(f"[发送@信息]{out_message}| [发送到] {recv['from']}")
            await self.bot.send_at_msg(recv["from"], out_message, [sign_wxid])

        else:  # 今天已签到，不加积分
            next_sign_in_date = datetime.strptime(signstat, "%Y%m%d") + timedelta(days=1)
            next_sign_in_date_formatted = next_sign_in_date.strftime("%Y年%m月%d日")
            out_message = f"\n-----XYBot-----\n❌你今天已经签到过了，每日凌晨刷新签到哦！下一次签到日期：{next_sign_in_date_formatted}"  # 创建信息
            logger.info(f"[发送@信息]{out_message}| [发送到] {recv['from']}")
            await self.bot.send_at_msg(recv["from"], out_message, [sign_wxid])

    def signstat_check(self, signstat):  # 检查签到状态
        signstat = "20000101" if signstat in ["0", "1"] else signstat
        last_sign_date = datetime.strptime(signstat, "%Y%m%d").date()
        now_date = datetime.now(tz=pytz.timezone(self.timezone)).date()
        return (now_date - last_sign_date).days >= 1
