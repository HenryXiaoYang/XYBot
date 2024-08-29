#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import os
import time

import aiohttp
import yaml
from loguru import logger

import pywxdll
from utils.plugin_interface import PluginInterface


class random_picture(PluginInterface):
    def __init__(self):
        config_path = "plugins/random_picture.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.random_picture_url = config["random_picture_url"]  # 随机图片api

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config["ip"]  # 机器人ip
        self.port = main_config["port"]  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

        cache_path = "resources/cache"  # 检测是否有cache文件夹
        if not os.path.exists(cache_path):
            logger.info("检测到未创建cache缓存文件夹")
            os.makedirs(cache_path)
            logger.info("已创建cache文件夹")

    async def run(self, recv):
        current_directory = os.path.dirname(os.path.abspath(__file__))

        cache_path_original = os.path.join(
            current_directory, f"../resources/cache/picture_{time.time_ns()}"
        )  # 图片缓存路径

        try:
            conn_ssl = aiohttp.TCPConnector(verify_ssl=False)
            async with aiohttp.request(
                    "GET", url=self.random_picture_url, connector=conn_ssl
            ) as req:
                cache_path = (
                        cache_path_original + req.headers["Content-Type"].split("/")[1]
                )
                with open(cache_path, "wb") as file:  # 下载并保存
                    file.write(await req.read())
                    file.close()
                await conn_ssl.close()

            logger.info(
                f'[发送信息](随机图图图片) {cache_path}| [发送到] {recv["from"]}'
            )
            self.bot.send_image_msg(
                recv["from"], os.path.abspath(cache_path)
            )  # 发送图片

        except Exception as error:
            out_message = f"-----XYBot-----\n出现错误❌！{error}"
            logger.error(error)
            logger.info(f'[发送信息]{out_message}| [发送到] {recv["from"]}')
            self.bot.send_text_msg(recv["from"], out_message)  # 发送
