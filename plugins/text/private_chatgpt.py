#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import re

import yaml
from loguru import logger
from openai import AsyncOpenAI
from wcferry import client

from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface
from wcferry_helper import XYBotWxMsg
from utils.ai_interface import OpenAIService, PoeService


class private_chatgpt(PluginInterface):
    def __init__(self):
        config_path = "plugins/text/private_chatgpt.yml"

        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f.read())

        self.enable_private_chat_gpt = config["enable_private_chat_gpt"]  # 是否开启私聊chatgpt

        self.gpt_version = config["gpt_version"]  # gpt版本
        self.gpt_max_token = config["gpt_max_token"]  # gpt 最大token
        self.gpt_temperature = config["gpt_temperature"]  # gpt 温度

        self.private_chat_gpt_price = config["private_chat_gpt_price"]  # 私聊gpt使用价格（单次）
        self.dialogue_count = config["dialogue_count"]  # 保存的对话轮数
        self.clear_dialogue_keyword = config["clear_dialogue_keyword"]

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.admins = main_config["admins"]  # 管理员列表

        # 从主配置读取 AI 服务类型,默认使用 openai
        self.ai_service_type = main_config.get("ai_service_type", "openai")
        
        # 根据服务类型选择性地读取配置
        if self.ai_service_type == "poe":
            self.poe_api_key = main_config["poe_api_key"]
            self.ai_service = PoeService(self.poe_api_key)
        else:  # 默认使用 openai
            self.openai_api_base = main_config["openai_api_base"]
            self.openai_api_key = main_config["openai_api_key"]
            self.ai_service = OpenAIService(self.openai_api_key, self.openai_api_base)

        sensitive_words_path = "sensitive_words.yml"  # 加载敏感词yml
        with open(sensitive_words_path, "r", encoding="utf-8") as f:  # 读取设置
            sensitive_words_config = yaml.safe_load(f.read())
        self.sensitive_words = sensitive_words_config["sensitive_words"]  # 敏感词列表

        self.db = BotDatabase()

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        if not self.enable_private_chat_gpt:
            return  # 如果不开启私聊chatgpt，不处理
        elif recv.from_group():
            return  # 如果是群聊消息，不处理

        recv.content = re.split(" |\u2005", recv.content) # 拆分消息

        # 这里recv.content中的内容是分割的
        gpt_request_message = " ".join(recv.content)
        wxid = recv.sender

        if gpt_request_message.startswith("我是"):  # 微信打招呼消息，不需要处理
            return

        error = ''
        if self.db.get_points(wxid) < self.private_chat_gpt_price and wxid not in self.admins and not self.db.get_whitelist(wxid):  # 积分不够
            error = f"您的积分不足 {self.private_chat_gpt_price} 点，无法使用私聊GPT功能！⚠️"
        elif not self.senstitive_word_check(gpt_request_message):  # 有敏感词
            error = "您的问题中包含敏感词，请重新输入！⚠️"

        if not error:  # 如果没有错误
            if recv.content[0] in self.clear_dialogue_keyword:  # 如果是清除对话记录的关键词，清除数据库对话记录
                self.clear_dialogue(wxid)  # 保存清除了的数据到数据库
                out_message = "对话记录已清除！✅"
                bot.send_text(out_message, wxid)
                logger.info(f'[发送信息]{out_message}| [发送到] {wxid}')
            else:
                gpt_answer = await self.chatgpt(wxid, gpt_request_message)  # 调用chatgpt函数
                if gpt_answer[0]:  # 如果没有错误
                    bot.send_text(gpt_answer[1], wxid)  # 发送回答
                    logger.info(f'[发送信息]{gpt_answer[1]}| [发送到] {wxid}')
                    if wxid not in self.admins and not self.db.get_whitelist(wxid):
                        self.db.add_points(wxid, -self.private_chat_gpt_price)  # 扣除积分，管理员不扣
                else:
                    out_message = f"出现错误⚠️！\n{gpt_answer[1]}"  # 如果有错误，发送错误信息
                    bot.send_text(out_message, wxid)
                    logger.error(f'[发送信息]{out_message}| [发送到] {wxid}')
        else:
            bot.send_text(error, recv.roomid)
            logger.info(f'[发送信息]{error}| [发送到] {wxid}')

    async def chatgpt(self, wxid: str, message: str):  # 这个函数请求了ai服务
        request_content = self.compose_gpt_dialogue_request_content(wxid, message)  # 构成对话请求内容，返回一个包含之前对话的列表

        try:
            success, response_content = await self.ai_service.chat_completion(
                messages=request_content,
                model=self.gpt_version,
                temperature=self.gpt_temperature,
                max_tokens=self.gpt_max_token
            )  # 调用ai服务，返回成功与否和回答内容

            if success:
                self.save_gpt_dialogue_request_content(wxid, request_content, response_content)
            return success, response_content

        except Exception as error:
            return False, error

    def compose_gpt_dialogue_request_content(self, wxid: str, new_message: str) -> list:
        json_data = self.db.get_private_gpt_data(wxid)  # 从数据库获得到之前的对话

        if not json_data or "data" not in json_data.keys():  # 如果没有对话数据，则初始化
            init_data = {"data": []}
            json_data = init_data

        previous_dialogue = json_data['data'][self.dialogue_count * -2:]  # 获取指定轮数的对话，乘-2是因为一轮对话包含了1个请求和1个答复
        request_content = [{"role": "system", "content": "You are a helpful assistant that output in plain text."}]
        request_content += previous_dialogue  # 将之前的对话加入到api请求内容中

        request_content.append({"role": "user", "content": new_message})  # 将用户新的问题加入api请求内容

        return request_content

    def save_gpt_dialogue_request_content(self, wxid: str, request_content: list, gpt_response: str) -> None:
        request_content.append({"role": "assistant", "content": gpt_response})  # 将gpt回答加入到api请求内容
        request_content = request_content[self.dialogue_count * -2:]  # 将列表切片以符合指定的对话轮数，乘-2是因为一轮对话包含了1个请求和1个答复

        json_data = {"data": request_content}  # 构成保存需要的json数据
        self.db.save_private_gpt_data(wxid, json_data)  # 保存到数据库中

    def senstitive_word_check(self, message):  # 检查敏感词
        for word in self.sensitive_words:
            if word in message:
                return False
        return True

    def clear_dialogue(self, wxid):  # 清除对话记录
        self.db.save_private_gpt_data(wxid, {"data": []})
