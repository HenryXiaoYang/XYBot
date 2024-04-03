#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import asyncio

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
        if (recv["content"][0] == self.command_prefix or self.command_prefix == "") and len(
                recv["content"]) != 1 and self.ignorance_check(recv):  # 判断是否为命令 判断是否不在屏蔽内
            if self.command_prefix != "":  # 特殊处理，万一用户想要使用空前缀
                recv["content"] = recv["content"][1:]  # 去除命令前缀
            recv["content"] = recv["content"].split(" ")  # 分割命令参数

            keyword = recv["content"][0]
            if keyword in plugin_manager.get_keywords().keys():
                plugin_func = plugin_manager.keywords[keyword]
                await asyncio.create_task(plugin_manager.plugins[plugin_func].run(recv))
            else:
                out_message = "该指令不存在！⚠️"
                logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
                self.bot.send_txt_msg(recv["wxid"], out_message)

    def ignorance_check(self, recv) -> bool:
        if self.ignorance_mode == 'none':  # 如果不设置屏蔽，则直接返回通过
            return True
        elif self.ignorance_mode == 'blacklist':  # 如果设置了黑名单
            # 如果是群与发送人不在黑名单内，或者不是群与发送人不在黑名单内，则返回通过
            if (recv['id1'] and (recv['wxid'] not in self.ignorance_blacklist)) or (
                    (not recv['id1']) and (recv['wxid'] not in self.ignorance_blacklist)):
                return True
            else:
                return False
        elif self.ignorance_mode == 'whitelist':
            # 如果是群与发送人在白名单内，或者不是群与发送人不在白名单内，则返回通过
            if (recv['id1'] and (recv['wxid'] in self.ignorance_whitelist)) or (
                    (not recv['id1']) and (recv['wxid'] in self.ignorance_whitelist)):
                return True
            else:
                return False
        else:
            raise Exception('Unknown ignorance mode 未知的屏蔽模式！')
