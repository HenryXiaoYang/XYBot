#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import os
import re
import time

import aiohttp
import yaml
from loguru import logger
from wcferry import client

from utils.plugin_interface import PluginInterface
from wcferry_helper import XYBotWxMsg


class random_picture(PluginInterface):
    def __init__(self):
        config_path = "plugins/command/random_picture.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.random_picture_url = config["random_picture_url"]  # 随机图片api

        self.cache_path = "resources/cache"

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        recv.content = re.split(" |\u2005", recv.content)  # 拆分消息

        # 图片缓存路径
        cache_path_original = os.path.abspath(os.path.join(self.cache_path, f"picture_{time.time_ns()}"))

        try:
            conn_ssl = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.request("GET", url=self.random_picture_url, connector=conn_ssl) as req:
                cache_path = cache_path_original + "." + str(req.url).split('.')[-1]  # 图片后缀
                with open(cache_path, "wb") as file:  # 下载并保存
                    file.write(await req.read())
                    file.close()

            await conn_ssl.close()

            logger.info(f'[发送信息](随机图图图片) {cache_path}| [发送到] {recv.roomid}')
            bot.send_image(os.path.abspath(cache_path), recv.roomid)  # 发送图片
            bot.send_pat_msg(recv.roomid, recv.sender)  # 发送拍一拍消息

        except Exception as error:
            out_message = f"-----XYBot-----\n出现错误❌！{error}"
            logger.error(error)
            logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid)  # 发送
