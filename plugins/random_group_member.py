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
            config = yaml.safe_load(f.read())

        self.member_count = config['member_count']

        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config['ip']  # 机器人ip
        self.port = main_config['port']  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

    async def run(self, recv):
        if recv['id1']:  # 判断是群还是私聊
            member_list = self.bot.get_chatroom_memberlist(recv['wxid'])['member']  # 获取群成员列表
            wxid_list = choices(member_list, k=self.member_count)  # 随机选取群成员

            # 组建信息
            out_message = '\n-----XYBot-----\n随机群成员❓：\n'
            for wxid in wxid_list:
                out_message += self.bot.get_chatroom_nickname(recv['wxid'], wxid)['nick'] + '\n'
            nick = self.bot.get_chatroom_nickname(recv['wxid'], recv['id1'])['nick']

            # 发送信息
            logger.info(
                '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_at_msg(recv['wxid'], recv['id1'], nick, out_message)
        else:  # 私聊
            out_message = '-----XYBot-----\n此功能仅可在群内使用！❌'
            logger.info(
                '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)
