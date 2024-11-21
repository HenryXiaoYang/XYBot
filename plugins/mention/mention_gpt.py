#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import base64
import json
import os
import time

import yaml
from loguru import logger
from openai import AsyncOpenAI
from wcferry import client

from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface
from wcferry_helper import XYBotWxMsg


class mention_gpt(PluginInterface):
    def __init__(self):
        config_path = "plugins/mention/mention_gpt.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.gpt_version = config["gpt_version"]  # gpt版本
        self.gpt_point_price = config["gpt_point_price"]  # gpt使用价格（单次）
        self.gpt_max_token = config["gpt_max_token"]  # gpt 最大token
        self.gpt_temperature = config["gpt_temperature"]  # gpt 温度

        self.model_name = config["model_name"]  # 模型名称
        self.image_quality = config["image_quality"]  # 图片质量
        self.image_size = config["image_size"]  # 图片尺寸
        self.image_price = config["image_price"]  # 图片价格

        self.max_possible_points = self.gpt_point_price * 2 + self.image_price  # 消耗积分极限

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.admins = main_config["admins"]  # 获取管理员列表

        self.openai_api_base = main_config["openai_api_base"]  # openai api 链接
        self.openai_api_key = main_config["openai_api_key"]  # openai api 密钥

        sensitive_words_path = "sensitive_words.yml"  # 加载敏感词yml
        with open(sensitive_words_path, "r", encoding="utf-8") as f:  # 读取设置
            sensitive_words_config = yaml.safe_load(f.read())
        self.sensitive_words = sensitive_words_config["sensitive_words"]  # 敏感词列表

        self.db = BotDatabase()

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        user_wxid = recv.sender
        gpt_request_message = recv.content

        error = ""
        if self.db.get_points(
                user_wxid) < self.max_possible_points and user_wxid not in self.admins and not self.db.get_whitelist(
            user_wxid):  # 积分不够
            error = f"本功能可消耗最多 {self.max_possible_points} 点积分，您的积分不足，无法使用GPT功能！⚠️"
        elif not self.senstitive_word_check(gpt_request_message):  # 有敏感词
            error = "您的问题中包含敏感词，请重新输入！⚠️"

        if error:
            await self.send_friend_or_group(bot, recv, error)
            return

        chat_completion = await self.chatgpt(gpt_request_message)

        if not chat_completion[0]:
            out_message = f"出现错误，请稍后再试！⚠️\n错误信息：\n{str(chat_completion[1])}"
            await self.send_friend_or_group(bot, recv, out_message)

        chat_completion = chat_completion[1]
        if chat_completion.choices[0].message.tool_calls:
            tool_call = chat_completion.choices[0].message.tool_calls[0]
            prompt = json.loads(tool_call.function.arguments).get("prompt")

            sucess = await self.generate_and_send_picture(prompt, bot, recv)

            chat_completion_2 = await self.function_call_result_to_gpt(gpt_request_message, prompt, sucess,
                                                                       chat_completion)
            await self.send_friend_or_group(bot, recv, chat_completion_2.choices[0].message.content)

            if user_wxid not in self.admins and not self.db.get_whitelist(user_wxid):
                minus_points = self.gpt_point_price * 2 + self.image_price
                self.db.add_points(user_wxid, minus_points * -1)

        else:
            await self.send_friend_or_group(bot, recv, chat_completion.choices[0].message.content)
            if user_wxid not in self.admins and not self.db.get_whitelist(user_wxid):
                self.db.add_points(user_wxid, self.gpt_point_price * -1)

    async def chatgpt(self, gpt_request_message):
        client = AsyncOpenAI(api_key=self.openai_api_key, base_url=self.openai_api_base)
        try:
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "generate_and_send_picture",
                        "description": "Generate an image using the user's description. Call this when the user requests an image, for example when a user asks 'Can you show me a picture of a cat?'. The function returns true on sucess.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "prompt": {
                                    "type": "string",
                                    "description": "The prompt of the image to generate."
                                },

                            },
                            "required": ["prompt"],
                            "additionalProperties": False
                        }
                    }
                }
            ]
            chat_completion = await client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful, creative, clever, and very friendly assistant. You output in plain text instead of markdown. You may also generate images.",
                    },
                    {
                        "role": "user",
                        "content": gpt_request_message,
                    }
                ],
                tools=tools,
                model=self.gpt_version,
                temperature=self.gpt_temperature,
                max_tokens=self.gpt_max_token,
            )
            return True, chat_completion
        except Exception as error:
            return False, error

    async def function_call_result_to_gpt(self, gpt_request_message, prompt, success, chat_completion):
        function_call_result_message = {
            "role": "tool",
            "content": json.dumps({
                "prompt": prompt,
                "success": success,
            }),
            "tool_call_id": chat_completion.choices[0].message.tool_calls[0].id
        }

        client = AsyncOpenAI(api_key=self.openai_api_key, base_url=self.openai_api_base)
        response_chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful, creative, clever, and very friendly assistant. You output in plain text instead of markdown. You may also generate images.",
                },
                {
                    "role": "user",
                    "content": gpt_request_message,
                },
                chat_completion.choices[0].message,
                function_call_result_message
            ],
            model=self.gpt_version,
            temperature=self.gpt_temperature,
            max_tokens=self.gpt_max_token,
        )
        return response_chat_completion

    async def generate_and_send_picture(self, prompt: str, bot: client.Wcf, recv: XYBotWxMsg) -> bool:
        try:
            save_path = await self.dalle3(prompt)
            bot.send_image(save_path, recv.roomid)
            return True
        except Exception as error:
            logger.error(f"Error: {error}")
            return False

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

    def senstitive_word_check(self, message):  # 检查敏感词
        for word in self.sensitive_words:
            if word in message:
                return False
        return True

    async def send_friend_or_group(self, bot: client.Wcf, recv: XYBotWxMsg, out_message="null"):
        if recv.from_group():  # 判断是群还是私聊
            out_message = f"@{self.db.get_nickname(recv.sender)}\n{out_message}"
            logger.info(f'[发送@信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid, recv.sender)  # 发送@信息

        else:
            logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid)  # 发送
