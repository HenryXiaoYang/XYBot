#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.
#
#  This program is licensed under the GNU General Public License v3.0.

import base64
import os

import pywxdll
import yaml
from loguru import logger

from plugin_interface import PluginInterface


class bot_status(PluginInterface):
    def __init__(self):
        config_path = os.path.abspath(__file__)[:-3] + '.yml'
        with open(config_path, 'r', encoding='utf-8') as f:  # 读取设置
            config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.status_message = config['status_message']

        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.bot_version = main_config['bot_version']

        self.ip = main_config['ip']
        self.port = main_config['port']
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

    def run(self, recv):
        b, a = [82, 50, 108, 48, 97, 72, 86, 105, 79, 105, 66, 111, 100, 72, 82, 119, 99, 122, 111, 118, 76, 50, 100,
                112, 100, 71, 104, 49, 89, 105, 53, 106, 98, 50, 48, 118, 83, 71, 86, 117, 99, 110, 108, 89, 97, 87, 70,
                118, 87, 87, 70, 117, 90, 121, 57, 89, 87, 85, 74, 118, 100, 65, 61, 61], ''
        for i in b: a += chr(i)
        out_message = "-----XYBot-----\n{status_message}\nBot version: {bot_version}\n{h}".format(
            status_message=self.status_message, bot_version=self.bot_version,
            h=base64.b64decode(a).decode("utf-8"))
        logger.info(
            '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
        self.bot.send_txt_msg(recv['wxid'], out_message)  # 发送
