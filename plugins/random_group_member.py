import os
from random import choices

import pywxdll
import yaml
from loguru import logger

from plugin_interface import PluginInterface


class random_group_member(PluginInterface):
    def __init__(self):
        config_path = os.path.abspath(__file__)[:-3] + '.yml'
        with open(config_path, 'r', encoding='utf-8') as f:  # 读取设置
            config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.member_count = config['member_count']

        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.ip = main_config['ip']
        self.port = main_config['port']
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

    def run(self, recv):
        if recv['id1']:
            member_list = self.bot.get_chatroom_memberlist(recv['wxid'])['member']
            wxid_list = choices(member_list, k=self.member_count)
            out_message = '\n-----XYBot-----\n随机群成员❓：\n'
            for wxid in wxid_list:
                out_message += self.bot.get_chatroom_nickname(recv['wxid'], wxid)['nick'] + '\n'
            nick = self.bot.get_chatroom_nickname(recv['wxid'], recv['id1'])['nick']
            logger.info(
                '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_at_msg(recv['wxid'], recv['id1'], nick, out_message)
        else:
            out_message = '-----XYBot-----\n此功能仅可在群内使用！❌'
            logger.info(
                '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)
