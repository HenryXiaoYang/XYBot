import os
import random

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

        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.ip = main_config['ip']
        self.port = main_config['port']
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api
        self.bot.start()  # 开启机器人

    def run(self, recv):
        self.db = BotDatabase()

        signin_points = random.randint(3, 20)  # 随机3-20积分
        signstat = self.db.get_stat(recv['id1'])  # 从数据库获取签到状态
        nickname = self.bot.get_chatroom_nick(recv['wxid'], recv['id1'])['content']['nick']  # 获取签到人昵称
        if signstat == 0:  # 如果今天未签到
            self.db.add_points(recv['id1'], signin_points)  # 在数据库加积分
            self.db.set_stat(recv['id1'], 1)  # 设置签到状态为已签到(1)
            out_message = '签到成功！你领到了{points}个积分！✅'.format(points=signin_points)  # 创建发送信息
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, out_message)  # 发送
        else:  # 今天已签到，不加积分
            out_message = '你今天已经签到过了！❌'  # 创建信息
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, out_message)  # 发送
