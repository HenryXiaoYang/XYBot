#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import asyncio
from datetime import datetime

import pytz
import requests
import schedule
import yaml
from loguru import logger
from wcferry import client

from utils.plans_interface import PlansInterface


class daily_greeting(PlansInterface):
    def __init__(self):
        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.timezone = main_config["timezone"]  # 时区

    async def job(self, bot: client.Wcf):
        week_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

        now = datetime.now(tz=pytz.timezone(self.timezone))

        date_str = now.strftime('%Y年%m月%d日')
        week_name = week_names[now.weekday()]
        daily_sentence = self.get_daily_sentence_formatted()

        message = f"早上好！☀️今天是{date_str} {week_name}。😆\n\n{daily_sentence}"

        contact_list = bot.get_contacts()
        for contact in contact_list:
            if str(contact.get("wxid")).endswith("@chatroom"):  # 是一个群聊
                bot.send_text(message, contact.get("wxid"))
                logger.info(f"[发送@信息]{message}| [发送到] {contact.get('wxid')}")

    @staticmethod
    def get_daily_sentence_formatted() -> str:
        hitokoto_api_url = "https://v1.hitokoto.cn/?encode=json&charset=utf-8"

        hitokoto_api_json = requests.get(hitokoto_api_url).json()

        sentence = hitokoto_api_json.get("hitokoto", "")
        from_type = hitokoto_api_json.get("from", "")
        from_who = hitokoto_api_json.get("from_who", "")

        if from_type:
            from_sentence = f"——{from_type} {from_who}"
        else:
            from_sentence = f"——{from_who}"

        formatted = f"「{sentence}」\n{from_sentence}"

        return formatted

    def job_async(self, bot: client.Wcf):
        loop = asyncio.get_running_loop()
        loop.create_task(self.job(bot))

    def run(self, bot: client.Wcf):
        schedule.every().day.at("07:00", tz=self.timezone).do(self.job_async, bot)
