#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import asyncio

import aiohttp
import yaml
from bs4 import BeautifulSoup
from loguru import logger

import pywxdll
from utils.plugin_interface import PluginInterface


class hypixel_info(PluginInterface):
    def __init__(self):
        config_path = "plugins/command/hypixel_info.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.bedwar_keywords = config["bedwar_keywords"]  # 获取查询bedwar小游戏关键词

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config["ip"]  # 机器人ip
        self.port = main_config["port"]  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

    async def run(self, recv):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE"
        }  # 设置user agent 绕cf

        # 指令格式错误判断
        if len(recv["content"]) == 1 or len(recv["content"]) > 3:
            out_message = "-----XYBot-----\n格式错误❌"

            await self.send_friend_or_group(recv, out_message)

        elif len(recv["content"]) == 2:  # Basic info
            await asyncio.create_task(self.send_basic_info(recv, headers))

        elif len(recv["content"]) == 3:
            if recv["content"][1] in self.bedwar_keywords:  # bedwar
                await asyncio.create_task(self.send_bedwar_info(recv, headers))

            else:
                out_message = "-----XYBot-----\n不存在的游戏！❌"
                await self.send_friend_or_group(recv, out_message)

    @staticmethod
    def check_valid(soup):
        for i in soup.find_all("h3", {"class": "m-t-0 header-title"}):
            if "Player Information" in i.get_text():
                return True
        return False

    @staticmethod
    def get_in_game_name(soup):  # 获取玩家游戏内名字 in game name
        # ign
        in_game_name = (
            soup.find("div", id="wrapper")
            .find("span", {"style": "font-family: 'Minecraftia', serif;"})
            .text
        )  # 爬虫查询，用css格式
        return in_game_name

    @staticmethod
    def get_basic_stats(soup):
        basic_stats = {}
        stats_bs4 = (
            soup.find("div", id="wrapper")
            .find_all("div", {"class": "card-box m-b-10"})[0]
            .find_all("b")[:-1]
        )  # 爬虫查询，用css格式
        for stat in stats_bs4:  # 从爬到的数据中提取
            basic_stats[stat.get_text() + " "] = (
                stat.next_sibling.strip()
            )  # 处理文本，去除空格特殊符号等
        return basic_stats

    @staticmethod
    def get_guild_stat(soup):
        # guild
        guild_stat = {}
        guild_bs4 = soup.find("div", id="wrapper").find_all(
            "div", {"class": "card-box m-b-10"}
        )[
            1
        ]  # 爬虫查询，用css格式
        if "Guild" in guild_bs4.get_text():  # 处理是否在公会中
            for info in guild_bs4.find_all("b"):  # 从爬到的数据中提取
                guild_stat[info.get_text().strip() + " "] = info.next_sibling.get_text(
                    separator="\n"
                )  # 处理文本，去除空格特殊符号等
        return guild_stat

    @staticmethod
    def get_status(soup):
        # status
        status = {}
        status_bs4 = soup.find("div", id="wrapper").find_all(
            "div", {"class": "card-box m-b-10"}
        )  # 爬虫查询，用css格式
        for i in status_bs4:  # 遍历查询结果
            if "Status" in i.get_text():  # 判断是否在线
                if "Offline" in i.get_text():
                    status["Status: "] = "Offline"

                    return status
                else:
                    status["Status: "] = "Online"
                    for info in i.find_all("b"):
                        status[info.get_text().strip() + ": "] = (
                            info.next_sibling.get_text()
                        )

                    return status

    @staticmethod
    def get_bedwar_stat(soup):
        # bw
        bw_stat = []
        table = soup.find("div", id="stat_panel_BedWars").find(
            "table", {"class": "table"}
        )  # 爬虫查询，用css格式
        for row in table.find_all("tr")[2:]:  # 遍历搜到的结果
            row_info_list = row.get_text(separator="#").split("#")  # 处理文本，去处#
            if row_info_list[0]:  # 判断结果是否有效
                bw_stat.append(row_info_list)
        return bw_stat

    async def send_friend_or_group(self, recv, out_message="null"):
        if recv["fromType"] == "chatroom":  # 判断是群还是私聊
            logger.info(f'[发送@信息]{out_message}| [发送到] {recv["from"]}')
            await self.bot.send_at_msg(recv["from"], "\n" + out_message, [recv["sender"]])

        else:
            logger.info(f'[发送信息]{out_message}| [发送到] {recv["from"]}')
            await self.bot.send_text_msg(recv["from"], out_message)  # 发送

    async def send_basic_info(self, recv, headers):
        request_ign = recv["content"][1]  # 请求的玩家ign (游戏内名字 in game name)

        await self.send_friend_or_group(recv, f"-----XYBot-----\n查询玩家 {request_ign} 中，请稍候！🙂")

        conn_ssl = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.request(
                "GET",
                url=f"http://plancke.io/hypixel/player/stats/{request_ign}",
                headers=headers,
                connector=conn_ssl,
        ) as req:
            soup = BeautifulSoup(await req.text(), "html.parser")
            await conn_ssl.close()

        if req.status != 404 and self.check_valid(soup):

            # basic info
            in_game_name = self.get_in_game_name(soup)
            basic_stats = self.get_basic_stats(soup)
            guild_stat = self.get_guild_stat(soup)
            status = self.get_status(soup)

            # 组建消息
            out_message = f"-----XYBot-----\n🎮玩家：\n{in_game_name}\n\n--------\n\n⚙️基础信息：\n"
            for key, value in basic_stats.items():
                out_message = out_message + key + value + "\n"
            out_message += "\n--------\n\n🏹公会信息：\n"
            for key, value in guild_stat.items():
                out_message = out_message + key + value + "\n"
            out_message += "\n--------\n\nℹ️当前状态：\n"
            for key, value in status.items():
                out_message = out_message + key + value + "\n"

            # 发送消息
            await self.send_friend_or_group(recv, out_message)

        else:  # 玩家不存在
            out_message = f"-----XYBot-----\n玩家 {request_ign} 不存在！❌"
            await self.send_friend_or_group(recv, out_message)

    async def send_bedwar_info(self, recv, headers):  # 获取玩家bedwar信息
        request_ign = recv["content"][2]  # 请求的玩家ign (游戏内名字 in game name)

        await self.send_friend_or_group(recv, f"-----XYBot-----\n查询玩家 {request_ign} 中，请稍候！🙂")  # 发送查询确认，让用户等待

        conn_ssl = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.request(
                "GET",
                url=f"http://plancke.io/hypixel/player/stats/{request_ign}",
                headers=headers,
                connector=conn_ssl,
        ) as req:
            soup = BeautifulSoup(await req.text(), "html.parser")
            await conn_ssl.close()

        if req.status != 404 and self.check_valid(soup):  # 判断响应是否有效

            in_game_name = self.get_in_game_name(soup)  # 从爬虫获取玩家真实ign
            bedwar_stat = self.get_bedwar_stat(soup)  # 从爬虫获取玩家bedwar信息

            # 组建信息
            out_message = f"-----XYBot-----\n🎮玩家：\n{in_game_name}\n\n--------\n\n🛏️起床战争信息：\n"
            table_header = [
                "⚔️模式：",
                "击杀：",
                "死亡：",
                "K/D：",
                "最终击杀：",
                "最终死亡：",
                "最终K/D：",
                "胜利：",
                "失败：",
                "W/L：",
                "破坏床数：",
            ]
            for row in bedwar_stat:
                for cell in range(len(row)):
                    out_message = out_message + table_header[cell] + row[cell] + "\n"
                out_message += "\n"

            # 发送
            await self.send_friend_or_group(recv, out_message)
        else:  # 玩家不存在
            out_message = f"-----XYBot-----\n玩家 {request_ign} 不存在！❌"
            await self.send_friend_or_group(recv, out_message)
