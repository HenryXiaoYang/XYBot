import asyncio

import pywxdll
import yaml
from loguru import logger

from plugin_manager import plugin_manager


class XYBot:
    def __init__(self):
        with open('main_config.yml', 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.load(f.read(), Loader=yaml.FullLoader)
        self.command_prefix = main_config['command_prefix']  # 命令前缀

        self.keywords = plugin_manager.get_keywords()

        self.ip = main_config['ip']  # 机器人ip
        self.port = main_config['port']  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

    async def message_handler(self, recv):
        if recv['content'][0] == self.command_prefix and len(recv['content']) != 1:  # 判断是否为命令
            recv['content'] = recv['content'][1:]  # 去除命令前缀
            recv['content'] = recv['content'].split(' ')  # 分割命令参数

            keyword = recv['content'][0]
            if keyword in plugin_manager.get_keywords().keys():
                plugin_func = plugin_manager.keywords[keyword]
                await asyncio.create_task(plugin_manager.plugins[plugin_func].run(recv))
            else:
                out_message = '该指令不存在！⚠️'
                logger.info(
                    '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
                self.bot.send_txt_msg(recv['wxid'], out_message)
