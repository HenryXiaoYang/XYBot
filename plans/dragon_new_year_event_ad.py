#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import os
from datetime import datetime
from zoneinfo import ZoneInfo

import pywxdll
import schedule
import yaml
from loguru import logger

from plans_interface import PlansInterface


class dragon_new_year_event_ad(PlansInterface):
    def __init__(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config['ip']
        self.port = main_config['port']
        self.timezone = main_config['timezone']
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

    def job(self):
        now = datetime.now(tz=ZoneInfo(self.timezone))  # 获取现在日期
        start = datetime.strptime('20240208', '%Y%m%d').replace(tzinfo=ZoneInfo(self.timezone))
        end = datetime.strptime('20240217', '%Y%m%d').replace(tzinfo=ZoneInfo(self.timezone))
        if start <= now <= end:
            contact_list = self.bot.get_contact_list()
            for user in contact_list:
                if user['wxid'][-9:] == '@chatroom' and user['wxid'] != '39023843820@chatroom':
                    out_message = '-----XYBot-----\n🎉XYBot龙年活动！🎉\n🐲成语接龙获得积分！🐲\n\n⚙️查看接龙详情\n指令：/接龙\n\n🥳参与接龙\n指令：/接龙 (成语)\n\n🎡活动开始时间：2024/2/10\n🎉活动结束时间：2024/2/17'
                    logger.info(f'[发送信息]{out_message}| [发送到] {user["wxid"]}')
                    self.bot.send_txt_msg(user['wxid'], out_message)

    def run(self):
        schedule.every(8).hours.do(self.job)
