import os

import pywxdll
import requests
import yaml
from loguru import logger

from plugin_interface import PluginInterface


class news(PluginInterface):
    def __init__(self):
        config_path = os.path.abspath(__file__)[:-3] + '.yml'
        with open(config_path, 'r', encoding='utf-8') as f:  # 读取设置
            config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.news_urls = config['news_urls']
        self.news_number = config['news_number']

        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.ip = main_config['ip']
        self.port = main_config['port']
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api
        self.bot.start()  # 开启机器人

    def run(self, recv):
        try:
            res = []
            for i in self.news_urls:  # 从设置中获取链接列表
                r = requests.get(i, timeout=5000, verify=False)  # 发送请求
                r.encoding = 'utf-8'
                res.append(r.json())
            out_message = '-----XYBot新闻-----\n'
            for j in res:  # 从新闻列表for
                for i in range(self.news_number):  # 从设置中获取单类新闻个数
                    dict_key = list(j.keys())
                    news_title = j[dict_key[0]][i].get('title', '❓未知❓')
                    news_type = j[dict_key[0]][i].get('tname', '❓未知❓')
                    news_source = j[dict_key[0]][i].get('source', '无😔')
                    news_description = j[dict_key[0]][i].get('digest', '无😔')
                    news_url = j[dict_key[0]][i].get('url', '无😔')

                    news_output = '{title}\n类型：{type}\n来源：{source}\n{description}...\n链接🔗：{url}\n----------\n'.format(
                        title=news_title, type=news_type, source=news_source, description=news_description,
                        url=news_url)  # 创建信息
                    out_message += news_output  # 加入最后输出字符串

            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)  # 发送

        except Exception as error:  # 错误处理
            out_message = '出现错误！⚠️{error}'.format(error=error)
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)
