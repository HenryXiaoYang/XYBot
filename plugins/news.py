from re import finditer

import aiohttp
import yaml
from bs4 import BeautifulSoup as bs
from html2text import html2text
from loguru import logger

import pywxdll
from utils.plugin_interface import PluginInterface


class news(PluginInterface):
    def __init__(self):
        config_path = "plugins/news.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.news_count = config["news_count"]  # 要获取的新闻数量

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config["ip"]  # 机器人ip
        self.port = main_config["port"]  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

    async def run(self, recv):
        try:
            url = 'https://i.news.qq.com/trpc.qqnews_web.kv_srv.kv_srv_http_proxy/list?sub_srv_id=24hours&srv_id=pc&offset=0&limit=190&strategy=1&ext={"pool":["top","hot"],"is_filter":7,"check_type":true}'
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}

            # 异步请求新闻数据
            conn_ssl = aiohttp.TCPConnector(verify_ssl=False)
            async with aiohttp.request('GET', url, headers=headers, connector=conn_ssl) as resp:
                news_list = await resp.json()
                await conn_ssl.close()

            out_message = '-----XYBot新闻-----'

            news_list = news_list["data"]["list"]

            for i in range(self.news_count):
                news_title = news_list[i]["title"]
                news_url = news_list[i]["url"]
                media_name = news_list[i]["media_name"]
                publish_time = news_list[i]["publish_time"]

                news_brief_content = await self.get_news_brief_content(news_url, news_title)

                out_message += f'\n\n📰 {news_title}\nℹ️{news_brief_content}......\n📺{media_name} {publish_time}\n🔗{news_url}'

            self.bot.send_txt_msg(recv['wxid'], out_message)
            logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
        except Exception as error:
            out_message = f'获取新闻失败!⚠️\n{error}'
            self.bot.send_txt_msg(recv['wxid'], out_message)
            logger.error(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')

    @staticmethod
    async def get_news_brief_content(url, news_title) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}
        conn_ssl = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.request('GET', url, headers=headers, connector=conn_ssl) as resp:
            news_raw_text = await resp.text()
            await conn_ssl.close()

        soup = bs(news_raw_text, "html.parser")
        news_text = str(soup.select("div.LEFT div.content.clearfix")[0])
        news_text = html2text(news_text).replace('\n', ' ').replace(news_title, '').strip()

        pattern = r"!\[\]\((.*?)\)"
        matches = finditer(pattern, news_text)
        for match in matches:
            news_text = news_text.replace(match.group(), '')

        return news_text[4:200]
