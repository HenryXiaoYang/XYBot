#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.
#
#  This program is licensed under the GNU General Public License v3.0.

import os
import random
from datetime import datetime
from zoneinfo import ZoneInfo

import pywxdll
import yaml
from loguru import logger

from database import BotDatabase
from plugin_interface import PluginInterface


class sign_in(PluginInterface):
    def __init__(self):
        config_path = os.path.abspath(__file__)[:-3] + '.yml'
        with open(config_path, 'r', encoding='utf-8') as f:  # 读取设置
            config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.min_points = config['min_points']  # 最小积分
        self.max_points = config['max_points']  # 最大积分

        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.ip = main_config['ip']  # 机器人ip
        self.port = main_config['port']  # 机器人端口
        self.timezone = main_config['timezone']  # 时区

        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

        self.db = BotDatabase()

    def run(self, recv):
        signin_points = random.randint(self.min_points, self.max_points)  # 随机3-20积分

        if recv['id1']:  # 判断是群还是私聊
            sign_wxid = recv['id1']  # 是群
        else:
            sign_wxid = recv['wxid']  # 是私聊

        signstat = str(self.db.get_stat(sign_wxid))  # 从数据库获取签到状态

        # pywxdll 0.1.8
        '''nickname = self.bot.get_chatroom_nick(recv['wxid'], recv['id1'])['content']['nick']  # 获取签到人昵称'''

        # pywxdll 0.2
        nickname = self.bot.get_chatroom_nickname(recv['wxid'], sign_wxid)['nick']  # 获取签到人昵称

        if self.signstat_check(signstat):  # 如果今天未签到
            self.db.add_points(sign_wxid, signin_points)  # 在数据库加积分
            now_datetime = datetime.now(tz=ZoneInfo(self.timezone)).strftime("%Y%m%d")  # 获取现在格式化后时间
            self.db.set_stat(sign_wxid, now_datetime)  # 设置签到状态为现在格式化后时间

            out_message = '\n-----XYBot-----\n签到成功！你领到了{points}个积分！✅'.format(points=signin_points)  # 创建发送信息
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, out_message)  # 发送

        else:  # 今天已签到，不加积分
            last_sign_date_formated = datetime.strptime(signstat, '%Y%m%d').strftime('%Y年%m月%d日')
            out_message = '\n-----XYBot-----\n❌你今天已经签到过了，每日凌晨刷新签到哦！上次签到日期：{last_sign_date_formated}'.format(
                last_sign_date_formated=last_sign_date_formated)  # 创建信息
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, out_message)  # 发送

    def signstat_check(self, signstat):  # 检查签到状态
        signstat = '20000101' if signstat in ['0', '1'] else signstat
        last_sign_date = datetime.strptime(signstat, '%Y%m%d').date()
        now_date = datetime.now(tz=ZoneInfo(self.timezone)).date()
        return (now_date - last_sign_date).days >= 1
