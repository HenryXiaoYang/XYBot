#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import asyncio

import xmltodict
import yaml
from loguru import logger

import pywxdll
from utils.plugin_manager import plugin_manager
from utils.private_chat_gpt import private_chat_gpt
from utils.singleton import singleton


@singleton
class XYBot:
    def __init__(self):
        with open("./main_config.yml", "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())
        self.command_prefix = main_config["command_prefix"]  # 命令前缀
        logger.debug(f"指令前缀为(如果是空则不会显示): {self.command_prefix}")

        self.keywords = plugin_manager.get_keywords()

        self.ip = main_config["ip"]  # 机器人ip
        self.port = main_config["port"]  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api
        logger.debug(f"机器人ip: {self.ip} 机器人端口: {self.port}")

        self.ignorance_mode = main_config['mode']
        self.ignorance_blacklist = main_config['blacklist']
        self.ignorance_whitelist = main_config['whitelist']

        self.enable_private_chat_gpt = main_config['enable_private_chat_gpt']

    async def message_handler(self, recv) -> None:
        if recv['type'] == 1:  # 是文本消息
            await self.text_message_handler(recv)

    async def text_message_handler(self, recv) -> None:
        # 预处理消息
        recv['signature'] = xmltodict.parse(recv['signature'].replace('\n', '').replace('\t', ''))

        if recv['fromUser'].endswith('@chatroom'):
            recv['fromType'] = 'chatroom'
        else:
            recv['fromType'] = 'friend'

        if recv['fromType'] == 'chatroom':
            split_result = recv['content'].split(":\n", 1)
            recv['sender'] = split_result[0]
            recv['content'] = split_result[1]
            recv['from'] = recv['fromUser']
            recv.pop('fromUser')

            recv['atUserList'] = recv.get('signature', {}).get('msgsource', {}).get('atuserlist', '')
            if recv['atUserList']:
                recv['atUserList'] = list(recv['atUserList'].split(','))
            else:
                recv['atUserList'] = []

        else:
            recv['sender'], recv['from'] = recv['fromUser']
            recv.pop('fromUser')

            recv['atUserList'] = []

        # 开始处理
        if not self.ignorance_check(recv):  # 判断是否不在屏蔽内
            return

        # 指令处理
        if recv["content"][0] == self.command_prefix or self.command_prefix == "":
            if self.command_prefix != "":  # 特殊处理，万一用户想要使用空前缀
                recv["content"] = recv["content"][1:]  # 去除命令前缀
            recv["content"] = recv["content"].split(" ")  # 分割命令参数

            keyword = recv["content"][0]
            if keyword in plugin_manager.get_keywords().keys():  # 是指令
                plugin_func = plugin_manager.keywords[keyword]
                await asyncio.create_task(plugin_manager.plugins[plugin_func].run(recv))
                return
            elif recv['fromType'] == 'chatroom' and self.command_prefix != "":  # 不是指令但在群里 且设置了指令前缀
                out_message = "该指令不存在！⚠️"
                logger.info(f'[发送信息]{out_message}| [发送到] {recv["from"]}')
                self.bot.send_text_msg(recv["from"], out_message)
                return

        # 私聊GPT，指令优先级大于GPT
        if (recv['content'][0] != self.command_prefix or self.command_prefix == "") and recv['fromType'] == "friend":
            if not isinstance(self.enable_private_chat_gpt, bool):
                raise Exception('Unknown enable_private_chat_gpt 未知的私聊gpt设置！')
            elif self.enable_private_chat_gpt is True:
                await asyncio.create_task(private_chat_gpt.run(recv))
                return

    def ignorance_check(self, recv) -> bool:
        if self.ignorance_mode == 'none':  # 如果不设置屏蔽，则直接返回通过
            return True
        elif self.ignorance_mode == 'blacklist':  # 如果设置了黑名单
            if recv['sender'] not in self.ignorance_blacklist:
                return True
            else:
                return False

        elif self.ignorance_mode == 'whitelist': # 白名单
            if recv['sender'] in self.ignorance_whitelist:
                return True
            else:
                return False

        else:
            logger.error("未知的屏蔽模式！请检查白名单/黑名单设置！")
