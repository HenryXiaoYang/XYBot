import os

import pywxdll
import yaml
from loguru import logger
from openai import OpenAI

from database import BotDatabase
from plugin_interface import PluginInterface


class gpt4(PluginInterface):
    def __init__(self):
        config_path = os.path.abspath(__file__)[:-3] + '.yml'
        with open(config_path, 'r', encoding='utf-8') as f:  # 读取设置
            config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.openai_api_base = config['openai_api_base']  # openai api 链接
        self.openai_api_key = config['openai_api_key']  # openai api 密钥
        self.gpt_version = config['gpt_version']  # gpt版本
        self.gpt_point_price = config['gpt_point_price']  # gpt使用价格（单次）
        self.gpt_max_token = config['gpt_max_token']
        self.gpt_temperature = config['gpt_temperature']

        current_directory = os.path.dirname(os.path.abspath(__file__))

        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.ip = main_config['ip']  # 机器人ip
        self.port = main_config['port']  # 机器人端口
        self.admins = main_config['admins']  # 管理员列表

        sensitive_words_path = os.path.join(current_directory, '../sensitive_words.yml')  # 加载敏感词yml
        with open(sensitive_words_path, 'r', encoding='utf-8') as f:  # 读取设置
            sensitive_words_config = yaml.load(f.read(), Loader=yaml.FullLoader)
        self.sensitive_words = sensitive_words_config['sensitive_words']  # 敏感词列表

        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人
        self.bot.start()  # 开启机器人

    def run(self, recv):
        self.db = BotDatabase()  # 放在init会不在一个线程上，数据库会报错

        if recv['id1']:  # 检查是群聊还是私聊
            is_chatgroup = True  # 是群聊
            user_wxid = recv['id1']  # 用户的wxid，非群聊id

            # pywxdll 0.1.8
            '''nickname = self.bot.get_chatroom_nick(recv['wxid'], recv['id1'])['content']['nick']  # 是群聊所以可以获取昵称'''

            # pywxdll 0.2
            nickname = self.bot.get_chatroom_nickname(recv['wxid'], recv['id1'])['nick']  # 是群聊所以可以获取昵称
        else:
            is_chatgroup = False  # 不是群聊
            user_wxid = recv['wxid']  # 用户的wxid，是私聊所以直接获得wxid
            nickname = ''  # 防止报错

        message = ' '.join(recv['content'][1:])  # 用户问题

        if (self.db.get_points(user_wxid) >= self.gpt_point_price or self.db.get_whitelist(
                user_wxid) == 1 or user_wxid in self.admins) and len(
            recv['content']) >= 2 and self.senstitive_word_check(
            message):  # 如果(积分足够或在白名单或在管理员)与指令格式正确与敏感词检查通过

            out_message = '-----XYBot-----\n已收到指令，处理中，请勿重复发送指令！👍'  # 发送已收到信息，防止用户反复发送命令
            logger.info(
                '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.send_friend_or_group(is_chatgroup, recv, user_wxid, nickname, out_message)  # 判断是群还是私聊

            if self.db.get_whitelist(user_wxid) == 1 or user_wxid in self.admins:  # 如果用户在白名单内/是管理员

                chatgpt_answer = self.chatgpt(message, recv)
                if chatgpt_answer[0]:
                    out_message = "-----XYBot-----\n因为你在白名单内，所以没扣除积分！👍\nChatGPT回答：\n{res}\n\n⚙️ChatGPT版本：{gpt_version}".format(
                        res=chatgpt_answer[1], gpt_version=self.gpt_version)  # 创建信息并从gpt api获取回答
                    logger.info(
                        '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
                    self.send_friend_or_group(is_chatgroup, recv, user_wxid, nickname, out_message)  # 判断是群还是私聊
                else:
                    out_message = '-----XYBot-----\n出现错误！⚠️{error}'.format(error=chatgpt_answer)
                    logger.info(
                        '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
                    self.send_friend_or_group(is_chatgroup, recv, user_wxid, nickname, out_message)  # 判断是群还是私聊

            elif self.db.get_points(user_wxid) >= self.gpt_point_price:  # 用户不在白名单内，并积分数大于等于chatgpt价格

                self.db.add_points(user_wxid, self.gpt_point_price * -1)
                chatgpt_answer = self.chatgpt(message, recv)

                if chatgpt_answer[0]:
                    out_message = "-----XYBot-----\n已扣除{gpt_price}点积分，还剩{points_left}点积分👍\nChatGPT回答：\n{res}\n\n⚙️ChatGPT版本：{gpt_version}".format(
                        gpt_price=self.gpt_point_price, points_left=self.db.get_points(user_wxid),  # 创建信息并从gpt api获取回答
                        res=chatgpt_answer[1], gpt_version=self.gpt_version)
                    logger.info(
                        '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
                    self.send_friend_or_group(is_chatgroup, recv, user_wxid, nickname, out_message)
                else:
                    self.db.add_points(user_wxid, self.gpt_point_price)
                    out_message = '-----XYBot-----\n出现错误，已补回积分！⚠️{error}'.format(error=chatgpt_answer)
                    logger.info(
                        '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
                    self.send_friend_or_group(is_chatgroup, recv, user_wxid, nickname, out_message)  # 判断是群还是私聊

        else:  # 参数数量不对
            out_message = '-----XYBot-----\n参数错误/积分不足,需要{require_points}点/内容包含敏感词⚠️'.format(
                require_points=self.gpt_point_price)
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))

            self.send_friend_or_group(is_chatgroup, recv, user_wxid, nickname, out_message)

    def chatgpt(self, message, recv):  # ChatGPT请求
        client = OpenAI(api_key=self.openai_api_key, base_url=self.openai_api_base)

        try:  # 防止崩溃
            response = client.chat.completions.create(
                model=self.gpt_version,
                messages=[{"role": "user", "content": message}],
                temperature=self.gpt_temperature,
                max_tokens=self.gpt_max_token
            )  # 用openai库创建请求
            return True, response.choices[0].message.content  # 返回答案
        except Exception as error:
            return False, error

    def senstitive_word_check(self, message):  # 检查敏感词
        for word in self.sensitive_words:
            if word in message:
                return False
        return True

    def send_friend_or_group(self, is_chatgroup, recv, user_wxid='null', nickname='null', out_message='null'):
        if is_chatgroup:  # 判断是群还是私聊
            self.bot.send_at_msg(recv['wxid'], user_wxid, nickname, '\n' + out_message)  # 发送
        else:
            self.bot.send_txt_msg(recv['wxid'], out_message)  # 发送
