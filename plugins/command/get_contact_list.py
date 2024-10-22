#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import os.path
import re
import time

import yaml
from loguru import logger
from openpyxl import Workbook
from wcferry import client

from utils.plugin_interface import PluginInterface
from wcferry_helper import XYBotWxMsg


class get_contact_list(PluginInterface):
    def __init__(self):
        config_path = "plugins/command/get_contact_list.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.excel_save_path = config["excel_save_path"]  # 保存路径

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.admin_list = main_config["admins"]  # 获取管理员列表

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        recv.content = re.split(" |\u2005", recv.content)  # 拆分消息

        admin_wxid = recv.sender

        if admin_wxid in self.admin_list:  # 判断操作人是否在管理员列表内
            wb = Workbook(write_only=True)
            xybot_contact_sheet = wb.create_sheet("XYBot通讯录")

            heading = ["wxid", "code", "remark", "name", "country", "province", "city", "gender"]
            xybot_contact_sheet.append(heading)

            contact_list = bot.get_contacts()

            for record in contact_list:  # 在通讯录数据中for
                wxid = record["wxid"]  # 获取wxid
                code = record["code"]  # 昵称
                remark = record["remark"]  # 微信定义的类型
                name = record["name"]  # 自定义微信号
                country = record["country"]
                province = record["province"]
                city = record["city"]
                gender = record["gender"]

                xybot_contact_sheet.append([wxid, code, remark, name, country, province, city, gender])  # 加入表格

            excel_path = f"{self.excel_save_path}/XYBotContact_{time.time_ns()}.xlsx"  # 保存路径
            wb.save(excel_path)  # 保存表格

            path = os.path.abspath(excel_path)

            logger.info(f'[发送文件]{path}| [发送到] {recv.roomid}')  # 发送
            bot.send_file(path, recv.roomid)  # 发送文件

        else:  # 用户不是管理员
            out_message = "-----XYBot-----\n❌你配用这个指令吗？"
            logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(recv.roomid, out_message)
