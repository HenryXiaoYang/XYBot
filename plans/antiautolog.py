import asyncio
import random

import schedule
import yaml
from loguru import logger
from wcferry import client

from utils.plans_interface import PlansInterface


class antiautolog(PlansInterface):
    def __init__(self):
        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())
        self.timezone = main_config["timezone"]

    async def job(self, bot: client.Wcf):
        out_message = f"防微信自动退出登录[{random.randint(1, 9999)}]"  # 组建信息
        logger.info(f'[发送信息]{out_message}| [发送到] {"filehelper"}')  # 直接发到文件传输助手，这样就不用单独键个群辣
        bot.send_text("filehelper", out_message)  # 发送

    def job_async(self, bot: client.Wcf):
        loop = asyncio.get_running_loop()
        loop.create_task(self.job(bot))

    def run(self, bot):
        schedule.every(10).minutes.do(self.job_async, bot)  # 每10分钟执行一次
