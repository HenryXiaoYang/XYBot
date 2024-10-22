#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import base64

import yaml
from loguru import logger
from wcferry import client

from utils.plugin_interface import PluginInterface
from wcferry_helper import XYBotWxMsg


class bot_status(PluginInterface):
    def __init__(self):
        config_path = "plugins/command/bot_status.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.status_message = config["status_message"]  # 状态信息

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.bot_version = main_config["bot_version"]

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        b, a = [
            82,
            50,
            108,
            48,
            97,
            72,
            86,
            105,
            79,
            105,
            66,
            111,
            100,
            72,
            82,
            119,
            99,
            122,
            111,
            118,
            76,
            50,
            100,
            112,
            100,
            71,
            104,
            49,
            89,
            105,
            53,
            106,
            98,
            50,
            48,
            118,
            83,
            71,
            86,
            117,
            99,
            110,
            108,
            89,
            97,
            87,
            70,
            118,
            87,
            87,
            70,
            117,
            90,
            121,
            57,
            89,
            87,
            85,
            74,
            118,
            100,
            65,
            61,
            61,
        ], ""  # 嘿嘿
        for i in b:
            a += chr(i)
        out_message = f"-----XYBot-----\n{self.status_message}\nBot version: {self.bot_version}\n{base64.b64decode(a).decode('utf-8')}"
        logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
        bot.send_text(out_message, recv.roomid)  # 发送
