#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.
#
#  This program is licensed under the GNU General Public License v3.0.

import json
import os

import pywxdll
import requests
import yaml
from loguru import logger
from prettytable import PrettyTable

from plugin_interface import PluginInterface


class get_chatroom_memberlist(PluginInterface):
    def __init__(self):
        config_path = os.path.abspath(__file__)[:-3] + '.yml'
        with open(config_path, 'r', encoding='utf-8') as f:  # 读取设置
            config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.information_post_url = config['information_post_url']

        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.ip = main_config['ip']
        self.port = main_config['port']
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

        self.admin_list = main_config['admins']

    def run(self, recv):
        if recv['id1'] in self.admin_list:  # 判断操作元是否是管理员
            heading = ['名字', 'wxid']
            chart = PrettyTable(heading)  # 创建列表

            # pywxdll 0.1.8
            ''' data = self.bot.get_chatroom_memberlist(recv['wxid'])  # 获取操作所在群的成员列表
            data = data['content']
            
            for i in data:  # for循环获得的数据
                if i['room_id'] == recv['wxid']:  # 如果群号相同
                    for j in i['member']:  # for循环成员列表
                        wxid = j
                        name = self.bot.get_chatroom_nick(recv['wxid'], j)['content']['nick']  # 获取成员昵称
                        chart.add_row([name, wxid])  # 加入表格中
            '''

            # pywxdll 0.2
            data = self.bot.get_chatroom_memberlist(recv['wxid'])

            for member_wxid in data['member']:  # for循环成员列表
                name = self.bot.get_chatroom_nickname(recv['wxid'], member_wxid)['nick']  # 获取成员昵称
                chart.add_row([name, member_wxid])  # 加入表格中

            chart.align = 'l'
            # 不传直接发微信是因为微信一行实在太少了，不同设备还不一样，用pywxdll发excel文件会报错
            json_data = json.dumps({"content": chart.get_string()})  # 转成json格式 用于发到api
            url = self.information_post_url + '/texts'  # 组建url
            headers = {"Content-Type": "application/json",
                       "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"}
            reqeust = requests.post(url, data=json_data, headers=headers, verify=False).json()  # 向api发送数据
            fetch_code = reqeust['fetch_code']  # 从api获取提取码
            date_expire = reqeust['date_expire']  # 从api获取过期时间

            fetch_link = '{url}/r/{code}'.format(url=self.information_post_url, code=fetch_code)  # 组建提取链接
            out_message = '-----XYBot-----\n🤖️本群聊的群员列表：\n{fetch_link}\n过期时间：{date_expire}'.format(
                fetch_link=fetch_link,
                date_expire=date_expire)  # 组建输出信息
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)  # 发送

        else:  # 操作人不是管理员
            out_message = '-----XYBot-----\n❌你配用这个指令吗？'
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)
