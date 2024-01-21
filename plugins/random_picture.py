#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.
#
#  This program is licensed under the GNU General Public License v3.0.

import os
import time

import pywxdll
import requests
import yaml
from loguru import logger

from plugin_interface import PluginInterface


class random_picture(PluginInterface):
    def __init__(self):
        config_path = os.path.abspath(__file__)[:-3] + '.yml'
        with open(config_path, 'r', encoding='utf-8') as f:  # 读取设置
            config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.random_picture_url = config['random_picture_url']

        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.ip = main_config['ip']
        self.port = main_config['port']
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

    def run(self, recv):
        current_directory = os.path.dirname(os.path.abspath(__file__))

        pic_cache_path_original = os.path.join(current_directory, '../resources/pic_cache/picture_{num}.'.format(
            num=time.time_ns()))

        try:
            r = requests.get(self.random_picture_url)
            pic_cache_path = pic_cache_path_original + r.headers['Content-Type'].split('/')[1]
            with open(pic_cache_path, 'wb') as f:  # 下载并保存
                f.write(r.content)
                f.close()

            logger.info(
                '[发送信息]{out_message} {path}| [发送到] {wxid}'.format(out_message="(随机图图图片) ",
                                                                         path=pic_cache_path, wxid=recv['wxid']))
            self.bot.send_pic_msg(recv['wxid'], os.path.abspath(pic_cache_path))  # 发送图片
        except Exception as error:
            out_message = '-----XYBot-----\n出现错误❌！{error}'.format(error=error)
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)  # 发送
