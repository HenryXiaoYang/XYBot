import aiohttp
import yaml
from bs4 import BeautifulSoup as bs
from loguru import logger

import pywxdll
from utils.plugin_interface import PluginInterface


class news(PluginInterface):
    def __init__(self):
        config_path = "plugins/news.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.important_news_count = config["important_news_count"]  # 要获取的要闻数量

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config["ip"]  # 机器人ip
        self.port = main_config["port"]  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

    async def run(self, recv):
        try:
            url = "https://news.china.com/#"
            conn_ssl = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.request('GET', url, connector=conn_ssl) as resp:
                news_html = await resp.text()
                await conn_ssl.close()

            soup = bs(news_html, "html.parser")

            focus_news = await self.get_focus_news(soup)
            focus_news_string = ""
            for title, link in focus_news:
                focus_news_string += f"📢{title}\n🔗{link}\n\n"

            important_news = await self.get_important_news(soup, self.important_news_count)
            important_news_string = ""
            for title, link, time in important_news:
                important_news_string += f"📰{title}\n🔗{link}\n🕒{time}\n\n"

            compose_message = f"----📰XYBot新闻📰----\n‼️‼️最新要闻‼️‼️\n{focus_news_string}\n⭐️⭐️要闻⭐️⭐️\n{important_news_string}"

            self.bot.send_text_msg(recv["from"], compose_message)
            logger.info(f'[发送信息]{compose_message}| [发送到] {recv["from"]}')

        except Exception as error:
            out_message = f'获取新闻失败!⚠️\n{error}'
            self.bot.send_text_msg(recv["from"], out_message)
            logger.error(f'[发送信息]{out_message}| [发送到] {recv["from"]}')

    @staticmethod
    async def get_focus_news(soup) -> list:  # 聚焦
        focus_news = []
        focus_soup = soup.html.body.select('.focus_side > h3 > a')

        for new in focus_soup:
            focus_news.append([new.get_text(), new.get('href')])

        return focus_news

    @staticmethod
    async def get_important_news(soup, count) -> list:  # 要闻
        important_news = []
        important_news_soup = soup.html.body.select('ul.item_list > li', limit=count)

        for new in important_news_soup:
            important_news.append([new.h3.a.get_text(), new.h3.a.get('href'), new.span.get_text(separator=' ')])

        return important_news
