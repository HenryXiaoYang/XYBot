import aiohttp
import yaml
from loguru import logger

import pywxdll
from utils.plugin_interface import PluginInterface


class random_picture_link(PluginInterface):
    def __init__(self):
        config_path = "plugins/random_picture_link.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.random_pic_link_url = config["random_pic_link_url"]  # 随机图片api url
        self.link_count = config["link_count"]  # 链接数量

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config["ip"]  # 机器人ip
        self.port = main_config["port"]  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

    async def run(self, recv):
        try:
            out_message = "-----XYBot-----\n❓❓❓\n"

            conn_ssl = aiohttp.TCPConnector(verify_ssl=False)
            for _ in range(self.link_count):
                async with aiohttp.request(
                        "GET", url=self.random_pic_link_url, connector=conn_ssl
                ) as req:
                    out_message += f"❓: {req.url}\n"
            await conn_ssl.close()

            logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')  # 发送信息
            self.bot.send_txt_msg(recv["wxid"], out_message)  # 发送


        except Exception as error:
            out_message = f"-----XYBot-----\n出现错误❌！{error}"
            logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
            self.bot.send_txt_msg(recv["wxid"], out_message)
