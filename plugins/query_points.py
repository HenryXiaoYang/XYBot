import os

import pywxdll
import yaml
from loguru import logger

from database import BotDatabase
from plugin_interface import PluginInterface


class query_points(PluginInterface):
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

        nickname = self.bot.get_chatroom_nick(recv['wxid'], recv['id1'])['content']['nick']  # 获取昵称
        out_message = '你有{}点积分！👍'.format(self.db.get_points(recv['id1']))  # 从数据库获取积分数并创建信息
        logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
        self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, out_message)  # 发送
