import os

import pywxdll
import yaml
from loguru import logger

from database import BotDatabase
from plugin_interface import PluginInterface


class points_leaderboard(PluginInterface):
    def __init__(self):
        config_path = os.path.abspath(__file__)[:-3] + '.yml'
        with open(config_path, 'r', encoding='utf-8') as f:  # 读取设置
            config = yaml.load(f.read(), Loader=yaml.FullLoader)

        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.ip = main_config['ip']
        self.port = main_config['port']
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api
        self.bot.start()  # 开启机器人

    def run(self, recv):
        self.db = BotDatabase()

        data = self.db.get_highest_points(30)  # 从数据库获取前30名积分数
        out_message = "-----XYBot积分排行榜-----"  # 创建积分
        rank = 1
        for i in data:  # 从数据库获取的数据中for循环
            nickname_req = self.bot.get_chatroom_nick(recv['wxid'], i[0])
            nickname = nickname_req['content']['nick']  # 获取昵称
            if nickname != nickname_req['content']['wxid']:
                out_message += "\n{rank}. {nickname} {points}分 👍".format(rank=rank, nickname=nickname,
                                                                          points=str(i[1]))
                rank += 1
        logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
        self.bot.send_txt_msg(recv['wxid'], out_message)
