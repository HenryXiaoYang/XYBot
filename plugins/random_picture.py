import os

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
        self.bot.start()  # 开启机器人

    def run(self, recv):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        pic_cache_path = os.path.join(current_directory, '../pic_cache/picture.png')  # 服务器的绝对路径，非客户端
        with open(pic_cache_path, 'wb') as f:  # 下载并保存
            r = requests.get(self.random_picture_url)
            f.write(r.content)
            f.close()
        logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message="(随机图图图片)", wxid=recv['wxid']))
        self.bot.send_pic_msg(recv['wxid'], os.path.abspath(pic_cache_path))  # 发送图片
