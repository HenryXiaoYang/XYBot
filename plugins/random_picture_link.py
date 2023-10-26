import os

import pywxdll
import requests
import yaml
from loguru import logger

from plugin_interface import PluginInterface


class random_picture_link(PluginInterface):
    def __init__(self):
        config_path = os.path.abspath(__file__)[:-3] + '.yml'
        with open(config_path, 'r', encoding='utf-8') as f:  # 读取设置
            config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.random_pic_link_url = config['random_pic_link_url']

        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.ip = main_config['ip']
        self.port = main_config['port']
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api
        self.bot.start()  # 开启机器人

    def run(self, recv):
        r = requests.get(self.random_pic_link_url, timeout=5000)  # 下载json
        r.encoding = 'utf-8'
        r = r.json()
        url_list = r['pics']
        out_message = '-----XYBot-----\n❓❓❓\n'  # 创建发送信息
        for i in range(1, len(url_list) + 1):
            out_message += '❓{num}：{url}\n'.format(num=i, url=url_list[i - 1])
        logger.info(
            '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))  # 发送信息
        self.bot.send_txt_msg(recv['wxid'], out_message)  # 发送
