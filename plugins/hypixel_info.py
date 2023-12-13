import os

import pywxdll
import requests
import yaml
from bs4 import BeautifulSoup
from loguru import logger

from plugin_interface import PluginInterface


class hypixel_info(PluginInterface):
    def __init__(self):
        config_path = os.path.abspath(__file__)[:-3] + '.yml'
        with open(config_path, 'r', encoding='utf-8') as f:  # 读取设置
            config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.bedwar_keywords = config['bedwar_keywords']

        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.ip = main_config['ip']
        self.port = main_config['port']
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api
        self.bot.start()  # 开启机器人

    def run(self, recv):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'}

        if len(recv['content']) == 1 or len(recv['content']) > 3:
            out_message = "-----XYBot-----\n格式错误❌"

            self.send_friend_or_group(recv, out_message)

        elif len(recv['content']) == 2:  # Basic info
            request_ign = recv['content'][1]

            self.send_friend_or_group(recv,
                                      '-----XYBot-----\n查询玩家 {request_ign} 中，请稍候！🙂'.format(
                                          request_ign=request_ign))

            req = requests.get('http://plancke.io/hypixel/player/stats/{request_ign}'.format(request_ign=request_ign),
                               headers=headers)
            soup = BeautifulSoup(req.text, 'html.parser')

            if req.status_code != 404 and self.check_valid(soup):

                # basic info
                in_game_name = self.get_in_game_name(soup)
                basic_stats = self.get_basic_stats(soup)
                guild_stat = self.get_guild_stat(soup)
                status = self.get_status(soup)

                out_message = '-----XYBot-----\n🎮玩家：\n{in_game_name}\n\n--------\n\n⚙️基础信息：\n'.format(
                    in_game_name=in_game_name)
                for key, value in basic_stats.items():
                    out_message = out_message + key + value + '\n'
                out_message += '\n--------\n\n🏹公会信息：\n'
                for key, value in guild_stat.items():
                    out_message = out_message + key + value + '\n'
                out_message += '\n--------\n\nℹ️当前状态：\n'
                for key, value in status.items():
                    out_message = out_message + key + value + '\n'

                self.send_friend_or_group(recv, out_message)

            else:
                out_message = '-----XYBot-----\n玩家 {request_ign} 不存在！❌'.format(request_ign=request_ign)
                self.send_friend_or_group(recv, out_message)

        elif len(recv['content']) == 3:
            if recv['content'][1] in self.bedwar_keywords:  # bedwar
                request_ign = recv['content'][2]

                self.send_friend_or_group(recv,
                                          '-----XYBot-----\n查询玩家 {request_ign} 中，请稍候！🙂'.format(
                                              request_ign=request_ign))

                req = requests.get(
                    'http://plancke.io/hypixel/player/stats/{request_ign}'.format(request_ign=request_ign),
                    headers=headers)
                soup = BeautifulSoup(req.text, 'html.parser')

                if req.status_code != 404 and self.check_valid(soup):

                    in_game_name = self.get_in_game_name(soup)
                    bedwar_stat = self.get_bedwar_stat(soup)
                    out_message = '-----XYBot-----\n🎮玩家：\n{in_game_name}\n\n--------\n\n🛏️起床战争信息：\n'.format(
                        in_game_name=in_game_name)
                    table_header = ['⚔️模式：', '击杀：', '死亡：', 'K/D：', '最终击杀：', '最终死亡：', '最终K/D：', '胜利：',
                                    '失败：', 'W/L：', '破坏床数：']
                    for row in bedwar_stat:
                        for cell in range(len(row)):
                            out_message = out_message + table_header[cell] + row[cell] + '\n'
                        out_message += '\n'

                    self.send_friend_or_group(recv, out_message)
                else:
                    out_message = '-----XYBot-----\n玩家 {request_ign} 不存在！❌'.format(request_ign=request_ign)
                    self.send_friend_or_group(recv, out_message)

            else:
                out_message = '-----XYBot-----\n不存在的游戏！❌'
                self.send_friend_or_group(recv, out_message)

    def check_valid(self, soup):
        for i in soup.find_all('h3', {'class': 'm-t-0 header-title'}):
            if 'Player Information' in i.get_text():
                return True
        return False

    def get_in_game_name(self, soup):
        # ign
        in_game_name = soup.find('div', id='wrapper').find('span',
                                                           {'style': "font-family: 'Minecraftia', serif;"}).text
        return in_game_name

    def get_basic_stats(self, soup):
        basic_stats = {}
        stats_bs4 = soup.find('div', id='wrapper').find_all('div', {'class': "card-box m-b-10"})[0].find_all('b')[:-1]
        for stat in stats_bs4:
            basic_stats[stat.get_text() + ' '] = stat.next_sibling.strip()
        return basic_stats

    def get_guild_stat(self, soup):
        # guild
        guild_stat = {}
        guild_bs4 = soup.find('div', id='wrapper').find_all('div', {'class': "card-box m-b-10"})[1]
        if 'Guild' in guild_bs4.get_text():
            for info in guild_bs4.find_all('b'):
                guild_stat[info.get_text().strip() + ' '] = info.next_sibling.get_text(separator='\n')
        return guild_stat

    def get_status(self, soup):
        # status
        status = {}
        status_bs4 = soup.find('div', id='wrapper').find_all('div', {'class': "card-box m-b-10"})
        for i in status_bs4:
            if 'Status' in i.get_text():
                if "Offline" in i.get_text():
                    status['Status: '] = 'Offline'

                    return status
                else:
                    status['Status: '] = 'Online'
                    for info in i.find_all('b'):
                        status[info.get_text().strip() + ': '] = info.next_sibling.get_text()

                    return status

    def get_bedwar_stat(self, soup):
        # bw
        bw_stat = []
        table = soup.find('div', id='stat_panel_BedWars').find('table', {'class': 'table'})
        for row in table.find_all('tr')[2:]:
            row_info_list = row.get_text(separator='#').split('#')
            if row_info_list[0]:
                bw_stat.append(row_info_list)
        return bw_stat

    def send_friend_or_group(self, recv, out_message='null'):
        if recv['id1']:  # 判断是群还是私聊
            logger.info(
                '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_at_msg(recv['wxid'], recv['id1'],
                                 self.bot.get_chatroom_nickname(recv['wxid'], recv['id1'])['nick'],
                                 '\n' + out_message)  # 发送
        else:
            logger.info(
                '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)  # 发送
