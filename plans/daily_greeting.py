#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

from datetime import datetime

import aiohttp
import pytz
import schedule
import yaml
from loguru import logger

import pywxdll
from utils.plans_interface import PlansInterface


class daily_greeting(PlansInterface):
    def __init__(self):
        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config["ip"]  # 机器人ip
        self.port = main_config["port"]  # 机器人端口
        self.timezone = main_config["timezone"]  # 时区
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

    def job(self):
        week_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

        now = datetime.now(tz=pytz.timezone(self.timezone))

        date_str = now.strftime('%Y年%m月%d日')
        week_name = week_names[now.weekday()]
        daily_sentence = self.get_daily_sentence_formatted()

        message = f"早上好！☀️今天是{date_str} {week_name}。😆\n\n{daily_sentence}"

        for contact in self.bot.get_contact_list():
            if str(contact.get("wxid")).endswith("@chatroom"):  # 是一个群聊
                self.bot.send_text_msg(contact.get("wxid"), message)
                logger.info(f"[发送@信息]{message}| [发送到] {contact.get('wxid')}")

    @staticmethod
    async def get_daily_sentence_formatted() -> str:
        hitokoto_api_url = "https://v1.hitokoto.cn/?encode=json&charset=utf-8"

        conn_ssl = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.request("GET", url=hitokoto_api_url, connector=conn_ssl) as response:
            hitokoto_api_json = await response.json()
            await conn_ssl.close()

        sentence = hitokoto_api_json.get("hitokoto")
        from_type = hitokoto_api_json.get("from")
        from_who = hitokoto_api_json.get("from_who")

        formatted = f"「{sentence}」\n       ——{from_type}·{from_who}"

        return formatted

    def run(self):
        schedule.every().day.at("07:00", tz=self.timezone).do(self.job)
