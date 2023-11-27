import os

import pywxdll
import yaml
from loguru import logger

import database
from plugin_interface import PluginInterface


class points_trade(PluginInterface):
    def __init__(self):
        config_path = os.path.abspath(__file__)[:-3] + '.yml'
        with open(config_path, 'r', encoding='utf-8') as f:  # 读取设置
            config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.max_points = config['max_points']
        self.min_points = config['min_points']

        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.ip = main_config['ip']
        self.port = main_config['port']
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api
        self.bot.start()  # 开启机器人

        self.db = database.BotDatabase()

    def run(self, recv):
        if recv['id1'] and len(recv['content']) >= 3 and recv['content'][1].isdigit():
            # 命令构造：/转帐 @(昵称) 积分数
            roomid = recv['wxid']

            trader_wxid = recv['id1']
            trader_nick = self.bot.get_chatroom_nickname(roomid, trader_wxid)['nick']
            trader_points = self.db.get_points(trader_wxid)

            target_nick = ' '.join(recv['content'][2:])[1:]
            target_nick = target_nick.replace('\u2005', '')  # 手机端微信会加个\u2005空格

            target_wxid = self.at_to_wxid_in_group(roomid, target_nick)

            points_num = int(recv['content'][1])

            error_message = ''

            if not target_wxid:
                error_message = '\n-----XYBot-----\n转帐失败❌\n转帐人不存在(仅可转账群内成员)或⚠️转帐目标昵称重复⚠️'
            elif not self.min_points <= points_num <= self.max_points:
                error_message = '\n-----XYBot-----\n转帐失败❌\n转帐积分无效(最大{max_points} 最小{min_points})'.format(
                    max_points=self.max_points, min_points=self.min_points)
            elif trader_points < points_num:
                error_message = '\n-----XYBot-----\n转帐失败❌\n积分不足😭'

            if not error_message:
                self.db.add_points(trader_wxid, points_num * -1)
                self.db.add_points(target_wxid, points_num)

                logger.success(
                    '[积分转帐]转帐人:{trader_wxid} {trader_nick}|目标:{target_wxid} {target_nick}|群:{roomid}|积分数:{points_num}'.format(
                        trader_wxid=trader_wxid, trader_nick=trader_nick, target_wxid=target_wxid,
                        target_nick=target_nick, roomid=roomid, points_num=points_num))

                trader_points = self.db.get_points(trader_wxid)
                target_points = self.db.get_points(target_wxid)

                out_message = '\n-----XYBot-----\n转帐成功✅! 你现在有{trader_points}点积分 {target_nick}现在有{target_points}点积分'.format(
                    trader_points=trader_points, target_nick=target_nick, target_points=target_points)
                logger.info(
                    '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=roomid))
                self.bot.send_at_msg(roomid, trader_wxid, trader_nick, out_message)

            else:
                logger.info(
                    '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=error_message, wxid=roomid))
                self.bot.send_at_msg(roomid, trader_wxid, trader_nick, error_message)
        else:
            out_message = '-----XYBot-----\n转帐失败❌\n指令格式错误/在私聊转帐积分(仅可在群聊中转帐积分)❌'
            logger.info(
                '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)

    def at_to_wxid_in_group(self, roomid, at):
        member_wxid_list = self.bot.get_chatroom_memberlist(roomid)['member']
        member_nick_to_wxid_dict = {}
        member_nick_list = []

        for wxid in member_wxid_list:
            nick = self.bot.get_chatroom_nickname(roomid, wxid)['nick']
            member_nick_to_wxid_dict[nick] = wxid
            member_nick_list.append(nick)

        if at in member_nick_to_wxid_dict.keys() and member_nick_list.count(at) == 1:
            return member_nick_to_wxid_dict[at]
        else:
            return None
