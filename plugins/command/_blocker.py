#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import asyncio

from loguru import logger
from wcferry import client

from utils.plugin_interface import PluginInterface
from wcferry_helper import XYBotWxMsg


class blocker(PluginInterface):
    def __init__(self):
        pass

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        logger.debug("开始执行blocker插件,10s")
        await asyncio.sleep(10)
        logger.debug("结束执行blocker插件")
