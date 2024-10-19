#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import re

import aiohttp
import yaml
from bs4 import BeautifulSoup as bs
from loguru import logger
from wcferry import client

from utils.plugin_interface import PluginInterface
from wcferry_helper import XYBotWxMsg


class news(PluginInterface):
    def __init__(self):
        config_path = "plugins/command/news.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.important_news_count = config["important_news_count"]  # 要获取的要闻数量

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        recv.content = re.split(" |\u2005", recv.content)  # 拆分消息

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

            bot.send_text(compose_message, recv.roomid)
            logger.info(f'[发送信息]{compose_message}| [发送到] {recv.roomid}')

        except Exception as error:
            out_message = f'获取新闻失败!⚠️\n{error}'
            bot.send_text(out_message, recv.roomid)
            logger.error(f'[发送信息]{out_message}| [发送到] {recv.roomid}')

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
