#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.
#
#  This program is licensed under the GNU General Public License v3.0.

import re

import aiohttp
import yaml
from loguru import logger
from wcferry import client

from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface
from wcferry_helper import XYBotWxMsg


class warthunder(PluginInterface):
    def __init__(self):
        config_path = "plugins/command/warthunder.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.command_format_menu = config["command_format_menu"]  # 指令格式

        self.warthunder_player_api_url = config["warthunder_player_api_url"]  # 要获取的要闻数量

        self.db = BotDatabase()

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        recv.content = re.split(" |\u2005", recv.content)  # 拆分消息

        error = ""
        if len(recv.content) < 2:
            error = f"-----XYBot-----\n参数错误!❌\n\n{self.command_format_menu}"

        if error:
            await self.send_friend_or_group(bot, recv, error)
            return

        player_name = ' '.join(recv.content[1:])
        await self.send_friend_or_group(bot, recv, f"-----XYBot-----\n正在查询玩家{player_name}的数据，请稍等...😄")

        data = await self.get_player_data(player_name)
        if isinstance(data, Exception):
            await self.send_friend_or_group(bot, recv, f"-----XYBot-----\n查询失败，错误信息：{data}")
            return
        elif data.get("error", False):
            await self.send_friend_or_group(bot, recv, f"-----XYBot-----\n目前API使用人数过多，请等候1分钟后再使用。🙏")
            return
        elif data.get("code", 200) == 404:
            await self.send_friend_or_group(bot, recv,
                                            f"-----XYBot-----\n未找到玩家{player_name}的数据，请检查昵称是否正确。🤔")
            return
        else:
            out_message = await self.parse_player_data(data)
            await self.send_friend_or_group(bot, recv, out_message)

    async def get_player_data(self, player_name):
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(60)) as session:
                async with session.get(f"{self.warthunder_player_api_url}{player_name}") as resp:
                    data = await resp.json()
            return data
        except Exception as e:
            return e

    @staticmethod
    async def parse_player_data(data):
        nickname = data.get("nickname")
        clan_name = data.get("clan_name")
        player_level = data.get("player_level")
        register_date = data.get("register_date")
        general_info = f"{clan_name} {nickname}\n等级：{player_level}级\n入坑战雷日期：{register_date}"

        realistic_data = data.get("statistics").get("realistic")
        realistic_battle_missions = realistic_data.get("CompletedMissions")
        realistic_winrate = realistic_data.get("VictoriesPerBattlesRatio")
        realistic_deaths = realistic_data.get("Deaths")
        realistic_sl_earned = realistic_data.get("LionsEarned")
        realistic_play_time = realistic_data.get("PlayTime")
        realistic_target_destroyed = realistic_data.get("AirTargetsDestroyed") + realistic_data.get(
            "GroundTargetsDestroyed") + realistic_data.get("NavalTargetsDestroyed")
        realistic_info = f"【历史性能】\n⚔️参与次数：{realistic_battle_missions}\n✌️胜率：{realistic_winrate}\n💀死亡数：{realistic_deaths}\n💥总击毁目标：{realistic_target_destroyed}\n🪙获得银狮：{realistic_sl_earned}\n⌛️游戏时间：{realistic_play_time}"

        aviation_rb_data = realistic_data.get("aviation")
        aviation_rb_battles = aviation_rb_data.get("AirBattle")
        aviation_rb_target_destroyed = aviation_rb_data.get("TotalTargetsDestroyed")
        aviation_tb_air_targets_destroyed = aviation_rb_data.get("AirTargetsDestroyed")
        aviation_rb_play_time = aviation_rb_data.get("TimePlayedInAirBattles")
        aviation_rb_info = f"【空战-历史性能】\n⚔️参与次数：{aviation_rb_battles}\n💥总击毁目标：{aviation_rb_target_destroyed}\n💥击毁空中目标：{aviation_tb_air_targets_destroyed}\n⌛️游戏时间：{aviation_rb_play_time}"

        ground_rb_data = realistic_data.get("ground")
        ground_rb_battles = ground_rb_data.get("GroundBattles")
        ground_rb_target_destroyed = ground_rb_data.get("TotalTargetsDestroyed")
        ground_rb_ground_targets_destroyed = ground_rb_data.get("GroundTargetsDestroyed")
        ground_rb_play_time = ground_rb_data.get("TimePlayedInGroundBattles")
        ground_rb_info = f"【陆战-历史性能】\n⚔️参与次数：{ground_rb_battles}\n💥总击毁目标：{ground_rb_target_destroyed}\n💥击毁地面目标：{ground_rb_ground_targets_destroyed}\n⌛️游戏时间：{ground_rb_play_time}"

        out_message = f"-----XYBot-----\n{general_info}\n\n{realistic_info}\n\n{aviation_rb_info}\n\n{ground_rb_info}"
        return out_message

    async def send_friend_or_group(self, bot: client.Wcf, recv: XYBotWxMsg, out_message="null"):
        if recv.from_group():  # 判断是群还是私聊
            out_message = f"@{self.db.get_nickname(recv.sender)}\n{out_message}"
            logger.info(f'[发送@信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid, recv.sender)  # 发送@信息
        else:
            logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid)  # 发送
