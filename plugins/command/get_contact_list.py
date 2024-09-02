#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import os.path
import time

import yaml
from loguru import logger
from openpyxl import Workbook

import pywxdll
from utils.plugin_interface import PluginInterface


class get_contact_list(PluginInterface):
    def __init__(self):
        config_path = "plugins/command/get_contact_list.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.excel_save_path = config["excel_save_path"]  # 保存路径

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config["ip"]  # 机器人ip
        self.port = main_config["port"]  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

        self.admin_list = main_config["admins"]  # 获取管理员列表

    async def run(self, recv):
        admin_wxid = recv["sender"]

        if admin_wxid in self.admin_list:  # 判断操作人是否在管理员列表内
            wb = Workbook(write_only=True)
            xybot_contact_sheet = wb.create_sheet("XYBot通讯录")

            heading = ["wxid", "nickname昵称", "type微信定义的类型", "类型", "customAccount自定义微信号"]
            xybot_contact_sheet.append(heading)

            contact_list = await self.bot.get_contact_list()

            for record in contact_list:  # 在通讯录数据中for
                wxid = record["wxid"]  # 获取wxid
                nickname = record["nickname"]  # 昵称
                wechat_type = record["type"]  # 微信定义的类型
                custom_account = record["customAccount"]  # 自定义微信号

                if wxid.endswith("@chatroom"):
                    type = "群"
                elif wxid.startswith("gh_"):
                    type = "公众号"
                elif wxid == "fmessage":
                    type = "朋友推荐消息"
                elif wxid == "medianote":
                    type = "语音记事本"
                elif wxid == "floatbottle":
                    type = "漂流瓶"
                elif wxid == "filehelper":
                    type = "文件传输助手"
                elif wxid.startswith("wxid_") or (wxid and custom_account != ""):
                    type = "好友"
                else:
                    type = "其他"

                xybot_contact_sheet.append([wxid, nickname, wechat_type, type, custom_account])  # 加入表格

            excel_path = f"{self.excel_save_path}/XYBot通讯录_{time.time_ns()}.xlsx"  # 保存路径
            wb.save(excel_path)  # 保存表格

            logger.info(f'[发送文件]{excel_path}| [发送到] {recv["from"]}')  # 发送
            await self.bot.send_file_msg(recv["from"], os.path.abspath(excel_path))  # 发送文件

        else:  # 用户不是管理员
            out_message = "-----XYBot-----\n❌你配用这个指令吗？"
            logger.info(f'[发送信息]{out_message}| [发送到] {recv["from"]}')
            await self.bot.send_text_msg(recv["from"], out_message)
