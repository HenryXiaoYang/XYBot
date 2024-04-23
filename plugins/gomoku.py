#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.
import asyncio
import os
from random import sample

import yaml
from PIL import Image, ImageDraw
from loguru import logger

import pywxdll
from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface


class gomoku(PluginInterface):
    def __init__(self):
        config_path = "plugins/gomoku.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.keywords = config["keywords"]
        self.create_game_sub_keywords = config["create_game_sub_keywords"]
        self.accept_game_sub_keywords = config["accept_game_sub_keywords"]
        self.play_game_sub_keywords = config["play_sub_keywords"]

        self.timeout = config['global_timeout']

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config["ip"]
        self.port = main_config["port"]
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

        self.db = BotDatabase()  # 实例化数据库类

        self.gomoku_games = {}  # 这个字典维护着所有的五子棋游戏
        self.gomoku_players = {}  # 这个字典维护着所有的五子棋玩家，用wxid查询是否已经在游戏中，以及对应的游戏id 游戏id为一个uuid

    async def run(self, recv):
        sub_keyword = recv["content"][1]

        if sub_keyword in self.create_game_sub_keywords:
            await self.create_game(recv)
        elif sub_keyword in self.accept_game_sub_keywords:
            await self.accept_game(recv)
        elif sub_keyword in self.play_game_sub_keywords:
            await self.play_game(recv)

    async def create_game(self, recv):
        error = ''
        if not recv["id1"]:  # 判断是否为群聊
            error = '-----XYBot-----\n❌请在群聊中游玩五子棋'
        elif len(recv['content']) < 3:  # 判断指令格式是否正确
            error = '-----XYBot-----\n❌指令格式错误'

        inviter_wxid = recv["id1"]

        if inviter_wxid in self.gomoku_players.keys():  # 判断是否已经在游戏中
            error = '-----XYBot-----\n❌您已经在一场游戏中了！'

        if not error:
            invitee_nick = ' '.join(recv['content'][2:])[1:].replace('\u2005', '')
            invitee_wxid = self.at_to_wxid_in_group(recv["wxid"], invitee_nick)

            if not invitee_wxid:
                error = '-----XYBot-----\n❌未找到对方！'
            elif invitee_wxid in self.gomoku_players.keys():
                error = '-----XYBot-----\n❌对方已经在一场游戏中或已经被邀请！'

            if error:
                self.send_friend_or_group(recv, error)
                return

            # 邀请五子棋游戏
            game_id = self.random_6_char()
            self.gomoku_players[inviter_wxid] = game_id
            self.gomoku_players[invitee_wxid] = game_id

            inviter_nick = self.bot.get_chatroom_nickname(recv["wxid"], inviter_wxid)["nick"]

            inviting_command = f'/{self.keywords[0]} {self.accept_game_sub_keywords[0]} {game_id}'
            out_message = f'-----XYBot-----\n🎉您收到了一份来自 {inviter_nick} 的五子棋比赛邀请！\n\n⚙️请在{self.timeout}秒内发送下面的指令来接受邀请：\n{inviting_command}'
            self.send_friend_or_group(recv, out_message, at_to_wxid=invitee_wxid)

            # 设置超时
            task = asyncio.create_task(self.timeout_accept_game(recv, game_id, inviter_wxid, invitee_wxid))

            # 保存游戏信息
            self.gomoku_games[game_id] = {
                'black': inviter_wxid,
                'white': invitee_wxid,
                'board': None,
                'turn': None,
                'status': 'inviting',
                'chatroom': recv['wxid'],
                'asyncio_task': task
            }
        else:
            self.send_friend_or_group(recv, error)

    async def accept_game(self, recv):
        error = ''
        if not recv["id1"]:  # 判断是否为群聊
            error = '-----XYBot-----\n❌请在群聊中游玩五子棋'
        elif len(recv['content']) < 3:  # 判断指令格式是否正确
            error = '-----XYBot-----\n❌指令格式错误'

        if not error:
            game_id = recv['content'][2]
            invitee_wxid = recv['id1']

            if game_id not in self.gomoku_games.keys():  # 判断游戏是否存在
                error = '-----XYBot-----\n❌该场五子棋游戏不存在！'
            elif self.gomoku_games[game_id]['white'] != invitee_wxid:  # 判断是否正确被邀请
                error = '-----XYBot-----\n❌您没被该场五子棋游戏邀请！'
            elif self.gomoku_games[game_id]['status'] != 'inviting':  # 判断游戏是否已经开始
                error = '-----XYBot-----\n❌该场五子棋游戏已经开始！'
            elif recv['wxid'] != self.gomoku_games[game_id]['chatroom']:  # 判断是否在同一个群聊
                error = '-----XYBot-----\n❌请在被邀请的群聊中接受邀请！'

            if error:
                self.send_friend_or_group(recv, error)
                return

            # 开始游戏
            self.gomoku_games[game_id]['asyncio_task'].cancel()  # 取消超时任务
            self.gomoku_games[game_id]['status'] = 'playing'

            # 初始化棋盘以及先后手
            self.gomoku_games[game_id]['board'] = [[0 for _ in range(17)] for _ in range(17)]
            self.gomoku_games[game_id]['turn'] = self.gomoku_games[game_id]['black']

            # 发送游戏开始信息
            inviter_nick = self.bot.get_chatroom_nickname(recv["wxid"], self.gomoku_games[game_id]['black'])["nick"]
            invitee_nick = self.bot.get_chatroom_nickname(recv["wxid"], self.gomoku_games[game_id]['white'])["nick"]
            out_message = f'-----XYBot-----\n🎉五子棋游戏 {game_id} 开始！\n\n⚫️黑方：{inviter_nick}\n⚪️白方：{invitee_nick}\n\n⚫️黑方先手！\n\n⏰每回合限时：{self.timeout}秒\n\n⚙️请发送下面指令落子:\n/{self.keywords[0]} {self.play_game_sub_keywords[0]} 横坐标纵坐标\n\n⚙️例如: /{self.keywords[0]} {self.play_game_sub_keywords[0]} C5'
            self.send_friend_or_group(recv, out_message)

            # 发送游戏棋盘图片
            board_image_path = self.draw_game_board(game_id)
            # 把路径转成绝对路径
            board_image_path = os.path.abspath(board_image_path)
            self.bot.send_pic_msg(self.gomoku_games[game_id]['chatroom'], board_image_path)
            logger.info(f'[发送信息](五子棋棋盘图片){board_image_path}| [发送到] {recv["wxid"]}')

            # 创建超时任务
            task = asyncio.create_task(self.timeout_play_game(recv, self.gomoku_games[game_id]['black'], game_id))
            self.gomoku_games[game_id]['asyncio_task'] = task

        else:
            self.send_friend_or_group(recv, error)
            return

    async def play_game(self, recv):
        error = ''
        if not recv["id1"]:
            error = '-----XYBot-----\n❌请在群聊中游玩五子棋'
        elif len(recv['content']) != 3:
            error = '-----XYBot-----\n❌指令格式错误'

        if not error:
            player_wxid = recv['id1']
            game_id = self.gomoku_players.get(player_wxid)
            # 这里都是与游戏场次相关的错误
            if player_wxid not in self.gomoku_players.keys() or not game_id:
                error = '-----XYBot-----\n❌您不在任何一场五子棋游戏中！'
            elif self.gomoku_games[game_id]['status'] != 'playing':
                error = '-----XYBot-----\n❌该场五子棋游戏已经结束或未开始！'
            elif self.gomoku_games[game_id]['black'] != player_wxid and self.gomoku_games[game_id][
                'white'] != player_wxid:
                error = '-----XYBot-----\n❌您不在该场五子棋游戏中！'
            elif player_wxid != self.gomoku_games[game_id]['turn']:
                error = '-----XYBot-----\n❌还没到您的回合！'

            # 这里都是与命令相关的错误
            elif recv['content'][2][0].upper() not in 'ABCDEFGHIJKLMNOPQ' or not recv['content'][2][1:].isdigit():
                error = '-----XYBot-----\n❌无效的落子坐标！'

            if error:
                self.send_friend_or_group(recv, error)
                return

            # 取消超时任务
            self.gomoku_games[game_id]['asyncio_task'].cancel()

            # 落子
            cord = recv['content'][2].upper()
            x = ord(cord[0]) - 65
            y = 16 - int(cord[1:])

            # 判断落子点是否在范围内
            if x < 0 or x > 16 or y < 0 or y > 16:
                error = '-----XYBot-----\n❌无效的落子坐标！'
                self.send_friend_or_group(recv, error)
                return

            # 判断棋盘上该坐标是否有棋子
            if self.gomoku_games[game_id]['board'][y][x] == 0:
                # 判断落子方
                if self.gomoku_games[game_id]['turn'] == self.gomoku_games[game_id]['black']:
                    self.gomoku_games[game_id]['board'][y][x] = 1
                    self.gomoku_games[game_id]['turn'] = self.gomoku_games[game_id]['white']
                elif self.gomoku_games[game_id]['turn'] == self.gomoku_games[game_id]['white']:
                    self.gomoku_games[game_id]['board'][y][x] = 2
                    self.gomoku_games[game_id]['turn'] = self.gomoku_games[game_id]['black']
            else:
                error = '-----XYBot-----\n❌该位置已经有棋子！'
                self.send_friend_or_group(recv, error)
                return

            # 发送游戏棋盘图片
            board_image_path = self.draw_game_board(game_id, highlight=(x, y))
            # 把路径转成绝对路径
            board_image_path = os.path.abspath(board_image_path)
            self.bot.send_pic_msg(self.gomoku_games[game_id]['chatroom'], board_image_path)
            logger.info(f'[发送信息](五子棋棋盘图片){board_image_path}| [发送到] {recv["wxid"]}')

            # 判断是否有人胜利
            winning = self.is_winning(game_id)
            if winning[0]:  # 有人胜利
                out_message = ''
                if winning[1] == 'black':
                    winner = self.gomoku_games[game_id]['black']
                    winner_nick = self.bot.get_chatroom_nickname(recv["wxid"], winner)["nick"]
                    out_message = f'-----XYBot-----\n🎉五子棋游戏 {game_id} 结束！🥳\n\n⚫️黑方：{winner_nick} 获胜！🏆'
                    logger.info(f'[五子棋]游戏 {game_id} 结束 | 胜利者：黑方 {winner}')
                elif winning[1] == 'white':
                    winner = self.gomoku_games[game_id]['white']
                    winner_nick = self.bot.get_chatroom_nickname(recv["wxid"], winner)["nick"]
                    out_message = f'-----XYBot-----\n🎉五子棋游戏 {game_id} 结束！🥳\n\n⚪️白方：{winner_nick} 获胜！🏆'
                    logger.info(f'[五子棋]游戏 {game_id} 结束 | 胜利者：白方 {winner}')
                elif winning[1] == 'draw':
                    out_message = f'-----XYBot-----\n🎉五子棋游戏 {game_id} 结束！🥳\n\n平局！⚖️'
                self.send_friend_or_group(recv, out_message)

                # 清除游戏
                self.gomoku_players.pop(self.gomoku_games[game_id]['black'])
                self.gomoku_players.pop(self.gomoku_games[game_id]['white'])
                self.gomoku_games.pop(game_id)

            else:
                # 发送落子信息
                player_nick = self.bot.get_chatroom_nickname(recv["wxid"], player_wxid)["nick"]
                player_emoji = '⚫️' if player_wxid == self.gomoku_games[game_id]['black'] else '⚪️'

                opponent_nick = self.bot.get_chatroom_nickname(recv["wxid"], self.gomoku_games[game_id]['turn'])["nick"]
                opponent_emoji = '⚫️' if self.gomoku_games[game_id]['turn'] == self.gomoku_games[game_id][
                    'black'] else '⚪️'

                out_message = f'-----XYBot-----\n {player_emoji}{player_nick} 把棋子落在了 {cord}！\n轮到 {opponent_emoji}{opponent_nick} 下子了！\n⏰限时：{self.timeout}秒\n\n⚙️请发送下面指令落子:\n/{self.keywords[0]} {self.play_game_sub_keywords[0]} 横坐标纵坐标\n\n⚙️例如: /{self.keywords[0]} {self.play_game_sub_keywords[0]} C5'
                self.send_friend_or_group(recv, out_message)

                # 创建超时任务
                task = asyncio.create_task(self.timeout_play_game(recv, player_wxid, game_id))
                self.gomoku_games[game_id]['asyncio_task'] = task



        else:
            self.send_friend_or_group(recv, error)
            return

    def draw_game_board(self, game_id, highlight=()):  # 绘制游戏棋盘
        gomoku_board_orignal_path = 'resources/gomoku_board_original.png'
        board_image = Image.open(gomoku_board_orignal_path)
        board_draw = ImageDraw.Draw(board_image)

        board_data = self.gomoku_games[game_id]['board']

        for y in range(17):
            for x in range(17):
                if board_data[y][x] == 1:  # 黑子
                    board_draw.ellipse((24 + x * 27 - 8, 24 + y * 27 - 8, 24 + x * 27 + 8,
                                        24 + y * 27 + 8), fill='black')
                elif board_data[y][x] == 2:  # 白子
                    board_draw.ellipse((24 + x * 27 - 8, 24 + y * 27 - 8, 24 + x * 27 + 8,
                                        24 + y * 27 + 8), fill='white')

        if highlight:
            board_draw.ellipse((24 + highlight[0] * 27 - 8, 24 + highlight[1] * 27 - 8, 24 + highlight[0] * 27 + 8,
                                24 + highlight[1] * 27 + 8), outline='red', width=2)

        saving_path = f'resources/pic_cache/gomoku_board_{game_id}.png'
        board_image.save(saving_path)  # 保存图片
        return saving_path  # 返回图片路径

    def is_winning(self, game_id):
        board = self.gomoku_games[game_id]['board']

        rows = len(board)
        cols = len(board[0])

        # 检查横向是否有五个连续的相同子
        for i in range(rows):
            for j in range(cols - 4):
                if board[i][j] == board[i][j + 1] == board[i][j + 2] == board[i][j + 3] == board[i][j + 4] != 0:
                    return (True, 'black') if board[i][j] == 1 else (True, 'white')

        # 检查纵向是否有五个连续的相同子
        for i in range(rows - 4):
            for j in range(cols):
                if board[i][j] == board[i + 1][j] == board[i + 2][j] == board[i + 3][j] == board[i + 4][j] != 0:
                    return (True, 'black') if board[i][j] == 1 else (True, 'white')

        # 检查左上到右下方向是否有五个连续的相同子
        for i in range(rows - 4):
            for j in range(cols - 4):
                if board[i][j] == board[i + 1][j + 1] == board[i + 2][j + 2] == board[i + 3][j + 3] == board[i + 4][
                    j + 4] != 0:
                    return (True, 'black') if board[i][j] == 1 else (True, 'white')

        # 检查右上到左下方向是否有五个连续的相同子
        for i in range(4, rows):
            for j in range(cols - 4):
                if board[i][j] == board[i - 1][j + 1] == board[i - 2][j + 2] == board[i - 3][j + 3] == board[i - 4][
                    j + 4] != 0:
                    return (True, 'black') if board[i][j] == 1 else (True, 'white')

        # 判断是否平局
        if all([all([board[i][j] != 0 for j in range(cols)]) for i in range(rows)]):
            return (True, 'draw')

        # 没有获胜者
        return (False, '')

    async def timeout_accept_game(self, recv, game_id, inviter_wxid, invitee_wxid):  # 邀请超时
        await asyncio.sleep(self.timeout)  # 等待超时
        # 判断是否还在游戏中
        if self.gomoku_players[inviter_wxid] == game_id and self.gomoku_players[
            invitee_wxid] == game_id and game_id in self.gomoku_games.keys() and self.gomoku_games[game_id][
            'status'] == 'inviting':
            # 清除这场五子棋游戏
            self.gomoku_players.pop(inviter_wxid)
            self.gomoku_players.pop(invitee_wxid)
            self.gomoku_games.pop(game_id)

            out_message = f'-----XYBot-----\n❌五子棋游戏 {game_id} 邀请超时！'  # 发送超时信息
            self.send_friend_or_group(recv, out_message, at_to_wxid=inviter_wxid)

    async def timeout_play_game(self, recv, player_wxid, game_id):  # 落子超时
        await asyncio.sleep(self.timeout)
        if self.gomoku_games[game_id]['status'] == 'playing' and player_wxid in self.gomoku_players:  # 判断是否还在游戏中
            # 清除这场五子棋游戏
            black_wxid = self.gomoku_games[game_id]['black']
            white_wxid = self.gomoku_games[game_id]['white']

            self.gomoku_players.pop(black_wxid)
            self.gomoku_players.pop(white_wxid)
            self.gomoku_games.pop(game_id)

            winner = white_wxid if player_wxid == black_wxid else black_wxid
            player_nick = self.bot.get_chatroom_nickname(recv["wxid"], player_wxid)["nick"]
            loser_nick = self.bot.get_chatroom_nickname(recv["wxid"], winner)["nick"]

            out_message = f'-----XYBot-----\n{loser_nick} 落子超时！\n🏆 {player_nick} 获胜！'  # 发送超时信息
            self.send_friend_or_group(recv, out_message, at_to_wxid=winner)

    def random_6_char(self) -> str:
        while True:
            chars = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q',
                     'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            char = "".join(sample(chars, 6))
            if char not in self.gomoku_games.keys():
                return char

    def send_friend_or_group(self, recv, out_message="null", at_to_wxid=''):
        if recv["id1"]:  # 判断是群还是私聊
            if not at_to_wxid:
                nickname = self.bot.get_chatroom_nickname(recv["wxid"], recv["id1"])["nick"]
            else:
                nickname = self.bot.get_chatroom_nickname(recv["wxid"], at_to_wxid)["nick"]
            logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
            self.bot.send_at_msg(
                recv["wxid"], recv["id1"], nickname, "\n" + out_message
            )  # 发送

        else:
            logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
            self.bot.send_txt_msg(recv["wxid"], out_message)  # 发送

    def at_to_wxid_in_group(self, roomid, at):  # 昵称转wxid
        # 这里尽力优化了
        member_wxid_list = self.bot.get_chatroom_memberlist(roomid)["member"]
        member_nick_to_wxid_dict = {
            self.bot.get_chatroom_nickname(roomid, wxid)["nick"]: wxid
            for wxid in member_wxid_list
        }

        return member_nick_to_wxid_dict.get(at)
