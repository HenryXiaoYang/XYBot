#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import asyncio
import re

import xmltodict
import yaml
from loguru import logger

import pywxdll
from utils.plugin_manager import plugin_manager
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

    async def message_handler(self, recv) -> None:
        message_type = recv.get('type', -1)
        if message_type == 1:  # 是文本消息
            await self.text_message_handler(recv)
        elif message_type == 3:  # 是图片消息
            await self.image_message_handler(recv)
        elif message_type == 34:  # 语音消息
            await self.voice_message_handler(recv)
        elif message_type == 10000:  # 系统消息
            await self.system_message_handler(recv)
        elif message_type == 10002:  # 撤回消息/拍一拍消息
            await self.revoke_or_pat_message_handler(recv)
        elif message_type == 47:  # 表情消息
            await self.emoji_message_handler(recv)
        elif message_type == 49:  # 很多消息都用了这个type，content里大量使用了xml，需要进一步判断
            await self.xml_message_handler(recv)
        else:  # 其他消息，type不存在或者还未知干啥用的
            logger.info(f"[其他消息] {recv}")

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
            recv['sender'] = recv['fromUser']
            recv['from'] = recv['fromUser']
            recv.pop('fromUser')

            recv['atUserList'] = []

        logger.info(f"[收到文本消息]:{recv}")

        # 开始处理
        if not self.ignorance_check(recv):  # 判断是否不在屏蔽内
            return

        # 指令处理
        if recv["content"][0] == self.command_prefix or self.command_prefix == "":
            if self.command_prefix != "":  # 特殊处理，万一用户想要使用空前缀
                recv["content"] = recv["content"][1:]  # 去除命令前缀

            recv["content"] = recv["content"].split(" ")  # 分割命令参数

            recv_keyword = recv["content"][0]
            for keyword in plugin_manager.get_keywords().keys():  # 遍历所有关键词
                if re.match(keyword, recv_keyword):  # 如果正则匹配到了，执行插件run函数
                    plugin_func = plugin_manager.keywords[keyword]
                    await asyncio.create_task(plugin_manager.plugins["command"][plugin_func].run(recv))
                    return

            if recv['fromType'] == 'chatroom' and self.command_prefix != "":  # 不是指令但在群里 且设置了指令前缀
                out_message = "该指令不存在！⚠️"
                logger.info(f'[发送信息]{out_message}| [发送到] {recv["from"]}')
                await self.bot.send_text_msg(recv["from"], out_message)
                return

        # text插件
        else:
            for plugin in plugin_manager.plugins["text"]:
                await asyncio.create_task(plugin.run(recv))

    async def image_message_handler(self, recv) -> None:
        # image插件调用
        for plugin in plugin_manager.plugins["image"]:
            await asyncio.create_task(plugin.run(recv))

    async def voice_message_handler(self, recv) -> None:
        for plugin in plugin_manager.plugins["voice"]:
            await asyncio.create_task(plugin.run(recv))

    async def system_message_handler(self, recv) -> None:
        logger.info(f"[收到系统消息]{recv}")

    async def revoke_or_pat_message_handler(self, recv) -> None:
        logger.info(f"[收到撤回/拍一拍消息]{recv}")

    async def emoji_message_handler(self, recv) -> None:
        logger.info(f"[收到表情消息]{recv}")

    async def xml_message_handler(self, recv) -> None:
        logger.info(f"[收到其他消息]{recv}")

    def ignorance_check(self, recv) -> bool:
        if self.ignorance_mode == 'none':  # 如果不设置屏蔽，则直接返回通过
            return True
        elif self.ignorance_mode == 'blacklist':  # 如果设置了黑名单
            if (recv["wxid"] not in self.ignorance_blacklist) and (recv["sender"] not in self.ignorance_blacklist):
                return True
            else:
                return False

        elif self.ignorance_mode == 'whitelist':  # 白名单
            if (recv["wxid"] in self.ignorance_whitelist) or (recv["sender"] in self.ignorance_whitelist):
                return True
            else:
                return False

        else:
            logger.error("未知的屏蔽模式！请检查白名单/黑名单设置！")
