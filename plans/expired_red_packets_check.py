import asyncio

import schedule
import yaml
from wcferry import client

from utils.plans_interface import PlansInterface
from utils.plugin_manager import plugin_manager


class expired_red_packets_check(PlansInterface):
    def __init__(self):
        config_path = "plugins/command/red_packet.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.max_time = config["max_time"]  # 红包超时时间

    async def job(self):
        if "red_packet" in plugin_manager.plugins.keys():
            plugin_manager.plugins["command"]["red_packet"].expired_red_packets_check()

    def job_async(self):
        loop = asyncio.get_running_loop()
        loop.create_task(self.job())

    def run(self, bot: client.Wcf):
        schedule.every(self.max_time).minutes.do(self.job_async)  # 每60分钟执行一次
