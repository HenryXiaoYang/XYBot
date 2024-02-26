import pywxdll
import yaml
from loguru import logger

from database import BotDatabase
from plugin_interface import PluginInterface


class points_leaderboard(PluginInterface):
    def __init__(self):
        config_path = 'plugins/points_leaderboard.yml'
        with open(config_path, 'r', encoding='utf-8') as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.leaderboard_top_number = config['leaderboard_top_number']  # 显示积分榜前x名人

        main_config_path = 'main_config.yml'
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config['ip']  # 机器人ip
        self.port = main_config['port']  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

        self.db = BotDatabase()  # 实例化数据库类

    async def run(self, recv):
        data = self.db.get_highest_points(self.leaderboard_top_number)  # 从数据库获取前x名积分数
        out_message = "-----XYBot积分排行榜-----"  # 创建积分
        rank = 1
        for i in data:  # 从数据库获取的数据中for循环
            nickname_req = self.bot.get_chatroom_nickname(recv['wxid'], i[0])
            nickname = nickname_req['nick']  # 获取昵称

            if nickname != nickname_req['wxid']:  # pywxdll 0.2
                out_message += f"\n{rank}. {nickname} {i[1]}分 👍"
                rank += 1
                # 组建积分榜信息

        logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
        self.bot.send_txt_msg(recv['wxid'], out_message)
