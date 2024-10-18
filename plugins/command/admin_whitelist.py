#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import yaml
from loguru import logger
from wcferry import client

from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface
from wcferry_helper import XYBotWxMsg


class admin_whitelist(PluginInterface):
    def __init__(self):
        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.admin_list = main_config["admins"]  # 获取管理员列表

        self.db = BotDatabase()  # 实例化数据库类

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        recv.content = recv.content.split(" |\u2005")  # 拆分消息

        admin_wxid = recv.sender  # 获取发送者wxid

        if recv.content[1].startswith('@'):  # 判断是@还是wxid
            wxid = recv.ats[-1]
        else:
            wxid = recv.content[1]  # 获取要操作的wxid

        action = recv.content[2]  # 获取操作
        if admin_wxid in self.admin_list:  # 如果操作人在管理员名单内
            if action == "加入":  # 操作为加入
                self.db.set_whitelist(wxid, 1)  # 修改数据库白名单信息
            elif action == "删除":  # 操作为删除
                self.db.set_whitelist(wxid, 0)  # 修改数据库白名单信息
            else:  # 命令格式错误
                out_message = "-----XYBot-----\n未知的操作❌"
                logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
                bot.send_text(out_message, recv.roomid)  # 发送信息

                return

            out_message = f"-----XYBot-----\n成功修改{wxid}的白名单！😊"
            logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid)  # 发送信息

        else:  # 操作人不在白名单内
            out_message = "-----XYBot-----\n❌你配用这个指令吗？"
            logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid)  # 发送信息
