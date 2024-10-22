#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import re

import aiohttp
import yaml
from loguru import logger
from wcferry import client

from utils.plugin_interface import PluginInterface
from wcferry_helper import XYBotWxMsg


class random_picture_link(PluginInterface):
    def __init__(self):
        config_path = "plugins/command/random_picture_link.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.random_pic_link_url = config["random_pic_link_url"]  # 随机图片api url
        self.link_count = config["link_count"]  # 链接数量

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        recv.content = re.split(" |\u2005", recv.content)  # 拆分消息

        try:
            out_message = "-----XYBot-----\n❓❓❓\n"

            conn_ssl = aiohttp.TCPConnector(verify_ssl=False)
            for _ in range(self.link_count):
                async with aiohttp.request(
                        "GET", url=self.random_pic_link_url, connector=conn_ssl
                ) as req:
                    out_message += f"❓: {req.url}\n"
            await conn_ssl.close()

            logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')  # 发送信息
            bot.send_text(out_message, recv.roomid)  # 发送

        except Exception as error:
            out_message = f"-----XYBot-----\n出现错误❌！{error}"
            logger.error(error)
            logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid)
