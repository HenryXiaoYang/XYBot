import yaml
from loguru import logger

import pywxdll
from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface


class admin_whitelist(PluginInterface):
    def __init__(self):
        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config["ip"]  # 机器人ip
        self.port = main_config["port"]  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

        self.admin_list = main_config["admins"]  # 获取管理员列表

        self.db = BotDatabase()  # 实例化数据库类

    async def run(self, recv):
        admin_wxid = recv["sender"]

        if recv['content'][1].startswith('@'):  # 判断是@还是wxid
            wxid = recv['atUserList'][0]
        else:
            wxid = recv["content"][1]  # 获取要操作的wxid

        action = recv["content"][2]  # 获取操作
        if admin_wxid in self.admin_list:  # 如果操作人在管理员名单内
            if action == "加入":  # 操作为加入
                self.db.set_whitelist(wxid, 1)  # 修改数据库白名单信息
            elif action == "删除":  # 操作为删除
                self.db.set_whitelist(wxid, 0)  # 修改数据库白名单信息
            else:  # 命令格式错误
                out_message = "-----XYBot-----\n未知的操作❌"
                logger.info(f'[发送信息]{out_message}| [发送到] {recv["from"]}')
                self.bot.send_text_msg(recv["from"], out_message)  # 发送信息

                return

            out_message = f"-----XYBot-----\n成功修改{wxid}的白名单！😊"
            logger.info(f'[发送信息]{out_message}| [发送到] {recv["from"]}')
            self.bot.send_text_msg(recv["from"], out_message)  # 发送信息

        else:  # 操作人不在白名单内
            out_message = "-----XYBot-----\n❌你配用这个指令吗？"
            logger.info(f'[发送信息]{out_message}| [发送到] {recv["from"]}')
            self.bot.send_text_msg(recv["from"], out_message)  # 发送信息
