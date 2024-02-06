import os

import pywxdll
import yaml
from loguru import logger

from database import BotDatabase
from plugin_interface import PluginInterface


class query_points(PluginInterface):
    def __init__(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config['ip']  # 机器人ip
        self.port = main_config['port']  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

        self.db = BotDatabase()  # 实例化机器人数据库类

    async def run(self, recv):
        if recv['id1']:  # 判断是群还是私聊
            query_wxid = recv['id1']  # 是群
        else:
            query_wxid = recv['wxid']  # 是私聊

        # pywxdll 0.1.8
        '''nickname = self.bot.get_chatroom_nick(recv['wxid'], recv['id1'])['content']['nick']  # 获取昵称'''

        # pywxdll 0.2
        nickname = self.bot.get_chatroom_nickname(recv['wxid'], recv['id1'])['nick']  # 获取昵称

        out_message = '-----XYBot-----\n你有{}点积分！👍'.format(self.db.get_points(query_wxid))  # 从数据库获取积分数并创建信息
        logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
        self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, out_message)  # 发送
