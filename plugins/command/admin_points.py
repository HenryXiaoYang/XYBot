#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import yaml
from loguru import logger

import pywxdll
from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface


class admin_points(PluginInterface):
    def __init__(self):
        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config["ip"]
        self.port = main_config["port"]
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

        self.admin_list = main_config["admins"]  # 获取管理员列表
        self.db = BotDatabase()  # 实例化数据库类

    async def run(self, recv):
        admin_wxid = recv["sender"]

        error = ''
        if admin_wxid not in self.admin_list:
            error = "-----XYBot-----\n❌你配用这个指令吗？"
        elif len(recv["content"]) < 3 or len(recv["content"]) > 4:
            error = "-----XYBot-----\n⚠️指令格式错误！"
        elif recv["content"][2] not in ["加", "减"] and len(recv["content"]) == 4:
            error = "-----XYBot-----\n⚠️未知的积分操作！"

        if not error:
            if recv['content'][1].startswith('@'): # 判断是@还是wxid
                change_wxid = recv['atUserList'][0]
            else:
                change_wxid = recv["content"][1]  # 获取要变更积分的wxid

            if len(recv["content"]) == 3:  # 直接改变，不加/减
                self.db.set_points(change_wxid, int(recv["content"][2]))
                await self.send_result(recv, change_wxid)
            elif recv["content"][2] == "加" and len(recv["content"]) == 4:  # 操作是加分
                self.db.add_points(change_wxid, int(recv["content"][3]))  # 修改积分
                await self.send_result(recv, change_wxid)

            elif recv["content"][2] == "减" and len(recv["content"]) == 4:  # 操作是减分
                self.db.add_points(
                    change_wxid, int(recv["content"][3]) * -1
                )  # 修改积分
                await self.send_result(recv, change_wxid)
            else:
                out_message = "-----XYBot-----\n⚠️未知的操作！"
                logger.info(f'[发送信息]{out_message}| [发送到] {recv["from"]}')
                await self.bot.send_text_msg(recv["from"], out_message)


        else:  # 操作人不在白名单内
            out_message = error
            logger.info(f'[发送信息]{out_message}| [发送到] {recv["from"]}')
            await self.bot.send_text_msg(recv["from"], out_message)

    async def send_result(self, recv, change_wxid):
        total_points = self.db.get_points(change_wxid)  # 获取修改后积分
        if len(recv['content']) == 4:
            out_message = f'-----XYBot-----\n😊成功给{change_wxid}{recv["content"][2]}了{recv["content"][3]}点积分！他现在有{total_points}点积分！'
        else:
            out_message = f'-----XYBot-----\n😊成功将{change_wxid}的积分设置为{total_points}！'
        logger.info(f'[发送信息]{out_message}| [发送到] {recv["from"]}')
        await self.bot.send_text_msg(recv["from"], out_message)  # 发送信息
