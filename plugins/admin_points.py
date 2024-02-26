import pywxdll
import yaml
from loguru import logger

from database import BotDatabase
from plugin_interface import PluginInterface


class admin_points(PluginInterface):
    def __init__(self):
        main_config_path = 'main_config.yml'
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config['ip']
        self.port = main_config['port']
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

        self.admin_list = main_config['admins']  # 获取管理员列表
        self.db = BotDatabase()  # 实例化数据库类

    async def run(self, recv):
        if recv['id1']:  # 用于判断是否为管理员
            admin_wxid = recv['id1']  # 是群
        else:
            admin_wxid = recv['wxid']  # 是私聊

        if admin_wxid in self.admin_list:
            change_wxid = recv['content'][1]  # 获取要变更积分的wxid

            if len(recv['content']) == 3:  # 直接改变，不加/减
                self.db.set_points(change_wxid, recv['content'][2])
                self.send_result(recv, change_wxid)

            elif recv['content'][2] == '加' and len(recv['content']) == 4:  # 操作是加分
                self.db.add_points(change_wxid, recv['content'][3])  # 修改积分
                self.send_result(recv, change_wxid)

            elif recv['content'][2] == '减' and len(recv['content']) == 4:  # 操作是减分
                self.db.add_points(change_wxid, int(recv['content'][3]) * -1)  # 修改积分
                self.send_result(recv, change_wxid)

        else:  # 操作人不在白名单内
            out_message = '-----XYBot-----\n❌你配用这个指令吗？'
            logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
            self.bot.send_txt_msg(recv['wxid'], out_message)

    def send_result(self, recv, change_wxid):
        total_points = self.db.get_points(change_wxid)  # 获取修改后积分
        out_message = f'-----XYBot-----\n😊成功给{change_wxid}{recv["content"][2]}了{recv["content"][3]}点积分！他现在有{total_points}点积分！'
        logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
        self.bot.send_txt_msg(recv['wxid'], out_message)  # 发送
