import aiohttp
import pywxdll
import yaml
from loguru import logger

from plugin_interface import PluginInterface


class news(PluginInterface):
    def __init__(self):
        config_path = 'plugins/news.yml'
        with open(config_path, 'r', encoding='utf-8') as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.news_urls = config['news_urls']  # 新闻url列表
        self.news_number = config['news_number']  # 要获取的新闻数量

        main_config_path = 'main_config.yml'
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config['ip']  # 机器人ip
        self.port = main_config['port']  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

    async def run(self, recv):
        try:
            res = []
            conn_ssl = aiohttp.TCPConnector(verify_ssl=False)
            for link in self.news_urls:  # 从设置中获取链接列表
                async with aiohttp.request('GET', url=link, connector=conn_ssl) as req:
                    res.append(await req.json())
            await conn_ssl.close()

            out_message = '-----XYBot新闻-----\n'
            for j in res:  # 从新闻列表for
                for i in range(self.news_number):  # 从设置中获取单类新闻个数
                    # 获取新闻的信息
                    dict_key = list(j.keys())
                    news_title = j[dict_key[0]][i].get('title', '❓未知❓')
                    news_type = j[dict_key[0]][i].get('tname', '❓未知❓')
                    news_source = j[dict_key[0]][i].get('source', '无😔')
                    news_description = j[dict_key[0]][i].get('digest', '无😔')
                    news_url = j[dict_key[0]][i].get('url', '无😔')

                    news_output = f'{news_title}\n类型：{news_type}\n来源：{news_source}\n{news_description}...\n链接🔗：{news_url}\n----------\n'
                    out_message += news_output  # 加入最后输出字符串

            logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
            self.bot.send_txt_msg(recv['wxid'], out_message)  # 发送

        except Exception as error:  # 错误处理
            out_message = f'出现错误！⚠️{error}'
            logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
            self.bot.send_txt_msg(recv['wxid'], out_message)
