#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.
#
#  This program is licensed under the GNU General Public License v3.0.

import base64
import os
import re
import time

import yaml
from loguru import logger
from openai import AsyncOpenAI
from wcferry import client

from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface
from wcferry_helper import XYBotWxMsg


class dalle3(PluginInterface):
    def __init__(self):
        config_path = "plugins/command/dalle3.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.price = config["price"]  # 每次使用的积分

        self.model_name = config["model_name"]  # dalle3模型
        self.image_quality = config["image_quality"]  # 生成的图片的质量
        self.image_size = config["image_size"]  # 生成的图片的大小
        self.image_style = config["image_style"]  # 生成的图片的风格

        self.command_format_menu = config["command_format_menu"]  # 帮助菜单

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.admins = main_config["admins"]  # 管理员列表

        self.openai_api_base = main_config["openai_api_base"]  # openai api 链接
        self.openai_api_key = main_config["openai_api_key"]  # openai api 密钥

        sensitive_words_path = "sensitive_words.yml"  # 加载敏感词yml
        with open(sensitive_words_path, "r", encoding="utf-8") as f:  # 读取设置
            sensitive_words_config = yaml.safe_load(f.read())
        self.sensitive_words = sensitive_words_config["sensitive_words"]  # 敏感词列表

        self.db = BotDatabase()

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        recv.content = re.split(" |\u2005", recv.content)  # 拆分消息

        user_wxid = recv.sender  # 获取发送者wxid
        user_request_prompt = " ".join(recv.content)

        error = ""
        if len(recv.content) < 2:  # 指令格式正确
            error = f"-----XYBot-----\n参数错误！🙅\n\n{self.command_format_menu}"
        # 检查积分是否足够，管理员与白名单不需要检查
        elif user_wxid not in self.admins and self.db.get_whitelist(user_wxid) == 0 and self.db.get_points(
                user_wxid) < self.price:
            error = f"-----XYBot-----\n积分不足！😭需要 {self.price} 点积分！"
        elif not self.senstitive_word_check(user_request_prompt):  # 敏感词检查
            error = "-----XYBot-----\n内容包含敏感词!⚠️"
        elif not user_request_prompt:
            error = f"-----XYBot-----\n请输入描述！🤔\n\n{self.command_format_menu}"

        if error:  # 如果没满足生成图片的条件，向用户发送为什么
            await self.send_friend_or_group(bot, recv, error)
            return

        await self.send_friend_or_group(bot, recv, "-----XYBot-----\n正在生成图片，请稍等...🤔")

        image_path = await self.dalle3(user_request_prompt)

        if isinstance(image_path, Exception):  # 如果出现错误，向用户发送错误信息
            await self.send_friend_or_group(bot, recv, f"-----XYBot-----\n出现错误，未扣除积分！⚠️\n{image_path}")
            return

        if user_wxid not in self.admins and self.db.get_whitelist(user_wxid) == 0:  # 如果用户不是管理员或者白名单，扣积分
            self.db.add_points(user_wxid, -self.price)
            await self.send_friend_or_group(bot, recv, f"-----XYBot-----\n🎉图片生成完毕，已扣除 {self.price} 点积分！🙏")

        bot.send_image(image_path, recv.roomid)
        logger.info(f'[发送图片]{image_path}| [发送到] {recv.roomid}')

    async def dalle3(self, prompt):  # 返回生成的图片的绝对路径，报错的话返回错误
        client = AsyncOpenAI(api_key=self.openai_api_key, base_url=self.openai_api_base)
        try:
            image_generation = await client.images.generate(
                prompt=prompt,
                model=self.model_name,
                n=1,
                response_format="b64_json",
                quality=self.image_quality,
                size=self.image_size)

            image_b64decode = base64.b64decode(image_generation.data[0].b64_json)
            save_path = os.path.abspath(f"resources/cache/dalle3_{time.time_ns()}.png")
            with open(save_path, "wb") as f:
                f.write(image_b64decode)
        except Exception as e:
            return e

        return save_path

    async def send_friend_or_group(self, bot: client.Wcf, recv: XYBotWxMsg, out_message: str):
        if recv.from_group():  # 判断是群还是私聊
            out_message = f"@{self.db.get_nickname(recv.sender)}\n{out_message}"
            logger.info(f'[发送@信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid, recv.sender)  # 发送@信息
        else:
            logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid)  # 发送信息

    def senstitive_word_check(self, message):  # 检查敏感词
        for word in self.sensitive_words:
            if word in message:
                return False
        return True
