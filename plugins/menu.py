import os

import pywxdll
import yaml
from loguru import logger

from plugin_interface import PluginInterface


class menu(PluginInterface):
    def __init__(self):
        config_path = os.path.abspath(__file__)[:-3] + '.yml'
        with open(config_path, 'r', encoding='utf-8') as f:  # 读取设置
            config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.main_menu = config['main_menu']
        self.menus = config['menus']

        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.ip = main_config['ip']
        self.port = main_config['port']

        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

    async def run(self, recv):
        if len(recv['content']) == 1:  # 如果命令列表长度为1，那就代表请求主菜单
            out_message = self.main_menu
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)
        elif recv['content'][1] in self.menus.keys():  # 长度不为1，发送以参数为键菜单内容为值的字典
            out_message = self.menus[recv['content'][1]]
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], self.menus[recv['content'][1]])
        else:
            out_message = '找不到此菜单!⚠️'  # 没找到对应菜单，发送未找到
            logger.info('[发送信息]' + out_message + ' | [发送到]' + recv['wxid'])
            self.bot.send_txt_msg(recv['wxid'], out_message)
