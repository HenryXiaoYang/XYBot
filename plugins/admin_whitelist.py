#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.
#
#  This program is licensed under the GNU General Public License v3.0.

import os

import pywxdll
import yaml
from loguru import logger

from database import BotDatabase
from plugin_interface import PluginInterface


class admin_whitelist(PluginInterface):
    def __init__(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.ip = main_config['ip']  # 机器人ip
        self.port = main_config['port']  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

        self.admin_list = main_config['admins']  # 获取管理员列表

        self.db = BotDatabase()  #实例化数据库类

    def run(self, recv):
        if recv['id1']:  # 判断是群还是私聊
            admin_wxid = recv['id1']  # 是群
        else:
            admin_wxid = recv['wxid']  # 是私聊

        wxid = recv['content'][1]  # 获取操作人
        action = recv['content'][2]  # 获取操作
        if admin_wxid in self.admin_list:  # 如果操作人在管理员名单内
            if action == '加入':  # 操作为加入
                self.db.set_whitelist(wxid, 1)  # 修改数据库白名单信息
            elif action == '删除':  # 操作为删除
                self.db.set_whitelist(wxid, 0)  # 修改数据库白名单信息
            else:  # 命令格式错误
                out_message = '-----XYBot-----\n未知的操作❌'
                logger.info(
                    '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
                self.bot.send_txt_msg(recv['wxid'], out_message)  #发送信息
                return

            out_message = '-----XYBot-----\n成功修改{}的白名单！😊'.format(wxid)
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)  #发送信息
        else:  # 操作人不在白名单内
            out_message = '-----XYBot-----\n❌你配用这个指令吗？'
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)  #发送信息
