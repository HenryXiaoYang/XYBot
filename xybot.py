import json
import os
import random

import openai
import pywxdll
import requests
import yaml
from loguru import logger
from prettytable import PrettyTable

import database


class XYBot:
    def __init__(self):

        with open('config.yml', 'r', encoding='utf-8') as f:  # 读取设置
            config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.ip = config['ip']  # 机器人API ip
        self.port = config['port']  # 机器人API 端口

        self.command_prefix = config['command_prefix']  # 机器人指令前缀

        self.menu_key = config['menu_key']  # 菜单关键词
        self.main_menu = config['main_menu']  # 主菜单
        self.menus = config['menus']  # 子菜单

        self.random_pic_link_key = config['random_pic_link_key']  # 随机链接关键词
        self.random_pic_link_url = config['random_pic_link_url']  # 随机链接链接

        self.random_pic_key = config['random_pic_key']  # 随机图图关键词
        self.random_pic_url = config['random_pic_url']  # 随机图图链接

        self.signin_key = config['signin_key']  # 签到关键词
        self.query_points_key = config['query_points_key']  # 查询积分关键词
        self.points_leaderboard_key = config['points_leaderboard_key']  # 积分榜关键词

        self.gpt_key = config['gpt_key']  # gpt关键词
        self.openai_api_base = config['openai_api_base']  # openai api 链接
        self.openai_api_key = config['openai_api_key']  # openai api 密钥
        self.gpt_version = config['gpt_version']  # gpt版本
        self.gpt_point_price = config['gpt_point_price']  # gpt使用价格（单次）

        self.admin_list = config['admins']  # 管理员列表

        self.admin_whitelist_key = config['admin_whitelist']  # 管理白名单关键词
        self.admin_points_key = config['admin_points']  # 管理积分关键词
        self.admin_signin_reset_key = config['admin_signin_reset']  # 重置签到状态关键词

        self.weather_key = config['weather_key']  # 天气查询关键词
        self.weather_api = config['weather_api']  # 天气查询链接
        self.weather_appid = config['weather_appid']  # 天气查询密钥
        self.weather_appsecret = config['weather_appsecret']  # 天气查询密钥

        self.news_key = config['news_key']  # 新闻查询关键词
        self.news_urls = config['news_urls']  # 新闻查询链接
        self.news_number = config['news_number']  # 单个类别新闻数

        self.information_post_url = config['information_post_url']  # 在线保存信息链接（用于获取机器人通讯录与获取群成员列表）

        self.get_contact_list_key = config['get_contact_list_key']  # 获取机器人通讯录关键词
        self.get_chatroom_memberlist_key = config['get_chatroom_memberlist_key']  # 获取群成员列表关键词

        self.db = database.BotDatabase()  # 机器人数据库

        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api
        self.bot.start()  # 开启机器人

    def handle_message(self, recv):
        if recv['content'][0] == self.command_prefix:  # 判断是否为命令
            recv['content'] = recv['content'][1:]  # 去除命令前缀
            recv['content'] = recv['content'].split(' ')  # 分割命令参数

            key = recv['content'][0]
            if recv['id1'] != '':
                if key in self.menu_key:  # 菜单
                    self.menu_handler(recv)
                elif key in self.random_pic_key:  # 随机图图
                    self.random_pic_handler(recv)
                elif key in self.random_pic_link_key:
                    self.random_pic_link_handler(recv)
                elif key in 'bottest':  # tmp
                    self.bot_test_handler(recv)
                elif key in self.signin_key:  # 签到
                    self.sign_in_handler(recv)
                elif key in self.query_points_key:  # 查询积分
                    self.query_points_handler(recv)
                elif key in self.points_leaderboard_key:  # 积分榜
                    self.points_leaderboard_handler(recv)
                elif key in self.gpt_key:  # ChatGPT
                    self.gpt_handler(recv)
                elif key in self.admin_whitelist_key:  # 管理白名单
                    self.admin_whitelist_handler(recv)
                elif key in self.admin_points_key:  # 管理积分
                    self.admin_points_handler(recv)
                elif key in self.admin_signin_reset_key:  # 重置签到状态
                    self.admin_signin_reset(recv)
                elif key in self.weather_key:  # 查询天气
                    self.weather_handler(recv)
                elif key in self.news_key:  # 查询新闻
                    self.news_handler(recv)
                elif key in self.get_contact_list_key:  # 获取机器人通讯录
                    self.get_contact_list_handler(recv)
                elif key in self.get_chatroom_memberlist_key:  # 获取当前群成员列表
                    self.get_chatroom_memberlist_handler(recv)
                else:
                    self.bot.send_txt_msg(recv['wxid'], '该指令不存在！')
            else:
                if recv['id1'] == '':
                    recv['id1'] = recv['wxid']  # 如果id1(朋友是空，群是发送人)是空，则id1为recv（即发送人）

                if key in self.menu_key:  # 菜单
                    self.menu_handler(recv)
                elif key in self.random_pic_key:  # 随机图图
                    self.random_pic_handler(recv)
                elif key in self.random_pic_link_key:  # 随机链接
                    self.random_pic_link_handler(recv)
                elif key in 'bottest':  # tmp
                    self.bot_test_handler(recv)
                elif key in self.signin_key:  # 签到
                    self.sign_in_handler(recv)
                elif key in self.query_points_key:  # 查询积分
                    self.query_points_handler(recv)
                elif key in self.points_leaderboard_key:  # 积分榜
                    self.points_leaderboard_handler(recv)
                elif key in self.gpt_key:  # ChatGPT
                    self.friend_chatgpt_handler(recv)
                elif key in self.admin_whitelist_key:  # 管理白名单
                    self.admin_whitelist_handler(recv)
                elif key in self.admin_points_key:  # 管理积分
                    self.admin_points_handler(recv)
                elif key in self.admin_signin_reset_key:  # 重置签到状态
                    self.admin_signin_reset(recv)
                elif key in self.weather_key:  # 查询天气
                    self.weather_handler(recv)
                elif key in self.news_key:  # 查询新闻
                    self.news_handler(recv)
                elif key in self.get_contact_list_key:  # 获取机器人通讯录
                    self.get_contact_list_handler(recv)
                elif key in self.get_chatroom_memberlist_key:  # 获取微信群成员列表
                    self.get_chatroom_memberlist_handler(recv)
                else:
                    self.bot.send_txt_msg(recv['wxid'], '该指令不存在！')

    def menu_handler(self, recv):  # 菜单
        if len(recv['content']) == 1:  # 如果命令列表长度为1，那就代表请求主菜单
            self.bot.send_txt_msg(recv['wxid'], self.main_menu)
        elif recv['content'][1] in self.menus.keys():  # 长度不为1，发送以参数为键菜单内容为值的字典
            out_message = self.menus[recv['content'][1]]
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], self.menus[recv['content'][1]])
        else:
            out_message = '找不到此菜单!⚠️'  # 没找到对应菜单，发送未找到
            logger.info('[发送信息]' + out_message + ' | [发送到]' + recv['wxid'])
            self.bot.send_txt_msg(recv['wxid'], out_message)

    def random_pic_handler(self, recv):  # 随机图图
        path = 'pic_cache/picture.png'  # 服务器的绝对路径，非客户端
        with open(path, 'wb') as f:  # 下载并保存
            r = requests.get(self.random_pic_url)
            f.write(r.content)
            f.close()
        logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message="(随机图图图片)", wxid=recv['wxid']))
        self.bot.send_pic_msg(recv['wxid'], os.path.abspath(path))  # 发送图片

    def random_pic_link_handler(self, recv):  # 随机链接
        r = requests.get(self.random_pic_link_url, timeout=5000)  # 下载json
        r.encoding = 'utf-8'
        r = r.json()
        url_list = r['pics']
        out_message = '-----XYBot-----\n❓❓❓\n'  # 创建发送信息
        for i in range(1, len(url_list) + 1):
            out_message += '❓{num}：{url}\n'.format(num=i, url=url_list[i - 1])
        logger.info(
            '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))  # 发送信息
        self.bot.send_txt_msg(recv['wxid'], out_message)  # 发送

    def bot_test_handler(self, recv):  # 测试用
        out_message = 'Bot running 😊'
        logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
        self.bot.send_txt_msg(recv['wxid'], out_message)

    def sign_in_handler(self, recv):  # 签到
        signin_points = random.randint(3, 20)  # 随机3-20积分
        signstat = self.db.get_stat(recv['id1'])  # 从数据库获取签到状态
        nickname = self.bot.get_chatroom_nick(recv['wxid'], recv['id1'])['content']['nick']  # 获取签到人昵称
        if signstat == 0:  # 如果今天未签到
            self.db.add_points(recv['id1'], signin_points)  # 在数据库加积分
            self.db.set_stat(recv['id1'], 1)  # 设置签到状态为已签到(1)
            out_message = '签到成功！你领到了{points}个积分！✅'.format(points=signin_points)  # 创建发送信息
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, out_message)  # 发送
        else:  # 今天已签到，不加积分
            out_message = '你今天已经签到过了！❌'  # 创建信息
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, out_message)  # 发送

    def query_points_handler(self, recv):  # 查询积分
        nickname = self.bot.get_chatroom_nick(recv['wxid'], recv['id1'])['content']['nick']  # 获取昵称
        out_message = '你有{}点积分！👍'.format(self.db.get_points(recv['id1']))  # 从数据库获取积分数并创建信息
        logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
        self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, out_message)  # 发送

    def points_leaderboard_handler(self, recv):  # 积分榜处理
        data = self.db.get_highest_points(10)  # 从数据库获取前10名积分数
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

    def chatgpt(self, message, recv):  # ChatGPT请求
        openai.api_key = self.openai_api_key  # 从设置中获取url和密钥
        openai.api_base = self.openai_api_base
        completion = ''  # 流传输稳定点
        try:
            response = openai.ChatCompletion.create(
                model=self.gpt_version,
                messages=[{"role": "user", "content": message}],
                stream=True,
            )
            for event in response:
                if event['choices'][0]['finish_reason'] == 'stop':
                    return completion
                res = event['choices'][0]['delta']
                if list(res.keys())[0] == 'content':
                    completion += res['content']
        except Exception as error:
            self.bot.send_txt_msg(recv['wxid'], '出现错误！⚠️{error}'.format(error=error))

    def gpt_handler(self, recv):  # ChatGPT处理
        nickname = self.bot.get_chatroom_nick(recv['wxid'], recv['id1'])['content']['nick']  # 获取昵称
        if len(recv['content']) >= 2:  # 如果命令格式正确
            message = '已收到指令，处理中，请勿重复发送指令！👍'  # 发送已收到信息，防止用户反复发送命令
            self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, message)  # 发送
            if self.db.get_whitelist(recv['id1']) == 1:  # 如果用户在白名单内
                message = ''  # 问题
                for i in recv['content'][1:]:
                    message = message + str(i) + ' '  # 获取用户问题，for循环是因为用户的指令件可能有空格
                out_message = "\n-----XYBot-----\n因为你在白名单内，所以没扣除积分！👍\nChatGPT回答：\n{res}".format(
                    res=self.chatgpt(message, recv))  # 创建信息并从gpt api获取回答
                logger.info(
                    '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
                self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, out_message)  # 发送
            elif self.db.get_points(recv['id1']) >= self.gpt_point_price:  # 用户不在白名单内，并积分数大于chatgpt价格
                message = ''  # 问题
                for i in recv['content'][1:]:
                    message = message + str(i) + ' '  # 获取用户问题
                self.db.minus_points(recv['id1'], self.gpt_point_price)
                out_message = "\n-----XYBot-----\n已扣除{gpt_price}点积分，还剩{points_left}点积分👍\nChatGPT回答：\n{res}".format(
                    gpt_price=self.gpt_point_price, points_left=self.db.get_points(recv['id1']),  # 创建信息并从gpt api获取回答
                    res=self.chatgpt(message, recv))
                logger.info(
                    '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
                self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, out_message)  # 发送信息
            else:  # 用户积分不够
                out_message = '积分不足！需要{}点！👎'.format(self.gpt_point_price)  # 创建信息
                logger.info(
                    '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
                self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, out_message)  # 发送
        else:  # 参数数量不对
            out_message = '参数错误！⚠️'
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, out_message)

    def friend_chatgpt_handler(self, recv):  # Chatgpt处理，同上，这个是用于私聊
        if len(recv['content']) >= 2:
            message = '已收到指令，处理中，请勿重复发送指令！👍'
            self.bot.send_txt_msg(recv['wxid'], message)
            if self.db.get_whitelist(recv['wxid']) == 1:
                message = ''
                for i in recv['content'][1:]:
                    message = message + str(i) + ' '
                out_message = "-----XYBot-----\n因为你在白名单内，所以没扣除积分！👍\nChatGPT回答：\n{res}".format(
                    res=self.chatgpt(message, recv))
                logger.info(
                    '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
                self.bot.send_txt_msg(recv['wxid'], out_message)
            elif self.db.get_points(recv['wxid']) >= self.gpt_point_price:
                message = ''
                for i in recv['content'][1:]:
                    message = message + str(i) + ' '
                self.db.minus_points(recv['wxid'], self.gpt_point_price)
                out_message = "-----XYBot-----\n已扣除{gpt_price}点积分，还剩{points_left}点积分👍\nChatGPT回答：\n{res}".format(
                    gpt_price=self.gpt_point_price, points_left=self.db.get_points(recv['wxid']),
                    res=self.chatgpt(message, recv))
                logger.info(
                    '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
                self.bot.send_txt_msg(recv['wxid'], out_message)
            else:
                out_message = "积分不足！👎需要{}点！".format(self.gpt_point_price)
                logger.info(
                    '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
                self.bot.send_txt_msg(recv['wxid'], out_message)
        else:
            out_message = '参数错误！⚠️'
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)

    def admin_whitelist_handler(self, recv):  # 管理白名单处理
        wxid = recv['content'][1]  # 获取操作人
        action = recv['content'][2]  # 获取操作
        if recv['id1'] in self.admin_list:  # 如果操作人在管理员名单内
            if action == '加入':  # 操作为加入
                self.db.set_whitelist(wxid, 1)  # 修改数据库白名单信息
            elif action == '删除':  # 操作为删除
                self.db.set_whitelist(wxid, 0)  # 修改数据库白名单信息
            else:  # 命令格式错误
                out_message = '未知的操作❌'
                logger.info(
                    '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
                self.bot.send_txt_msg(recv['wxid'], out_message)
                return

            out_message = '成功修改{}的白名单！😊'.format(wxid)
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)
        else:  # 操作人不在白名单内
            out_message = '❌你配用这个指令吗？'
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)

    def admin_points_handler(self, recv):  # 管理积分处理
        wxid = recv['content'][1]  # 获取操作人
        action = recv['content'][2]  # 获取操作
        if recv['id1'] in self.admin_list:  # 如果操作人在白名单内
            if len(recv['content']) == 3:  # 命令长度为3 则直接设置积分数
                self.db.set_points(wxid, int(action))
            elif action == '加':  # 命令长度不为为3 判断操作是加 加积分数
                self.db.add_points(wxid, int(recv['content'][3]))
            elif action == '减':  # 命令长度不为为3 判断操作是减 减积分数
                self.db.minus_points(wxid, int(recv['content'][3]))
            else:  # 命令参数错误
                self.bot.send_txt_msg(recv['wxid'], '参数错误！{action}'.format(action=action))
                logger.debug('管理积分参数错误！⚠️{action}'.format(action=action))
                return

            total_points = self.db.get_points(wxid)  # 获取修改后积分
            fmsg = '😊成功给{wxid}{action}了{points}点积分！他现在有{total}点积分！'  # 创建信息
            out_message = fmsg.format(wxid=wxid, action=action, points=recv['content'][3], total=total_points)
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)  # 发送
        else:  # 操作人不在白名单内
            out_message = '❌你配用这个指令吗？'
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)

    def admin_signin_reset(self, recv):  # 重置数据库签到状态
        if recv['id1'] in self.admin_list:  # 如果操作人在白名单内
            self.db.reset_stat()  # 重置数据库签到状态
            out_message = '😊成功重置签到状态！'
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)
        else:  # 操作人不在白名单内
            out_message = '❌你配用这个指令吗？'
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)

    def weather_handler(self, recv):  # 天气查询
        city = recv['content'][1]  # 获取要查询的天气
        url = "{api}?appid={appid}&appsecret={appsecret}&unescape=1&city={city}".format(api=self.weather_api,
                                                                                        appid=self.weather_appid,
                                                                                        appsecret=self.weather_appsecret,
                                                                                        city=city)  # 从设置中获取链接，密钥，并构成url
        try:
            r = requests.get(url, timeout=5000)  # 向url发送请求
            r.encoding = 'utf-8'
            res = r.json()
            out_message = '-----XYBot-----\n城市🌆：{city}\n天气☁️：{weather}\n实时温度🌡️：{temp}°\n白天温度🌡：{temp_day}°\n夜晚温度🌡：{temp_night}°\n空气质量🌬：{air_quality}\n空气湿度💦：{air_humidity}\n风向🌬：{wind_speed}{wind_dir}\n更新时间⌚：{update_time}'.format(
                city=res['city'], weather=res['wea'], temp=res['tem'], temp_day=res['tem_day'],
                temp_night=res['tem_night'], air_quality=res['air'], air_humidity=res['humidity'], wind_dir=res['win'],
                wind_speed=res['win_speed'], update_time=res['update_time'])  # 创建信息
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)
        except Exception as error:  # 报错处理
            out_message = '出现错误！⚠️{error}'.format(error=error)
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)

    def news_handler(self, recv):  # 新闻查询
        try:
            res = []
            for i in self.news_urls:  # 从设置中获取链接列表
                r = requests.get(i, timeout=5000)  # 发送请求
                r.encoding = 'utf-8'
                res.append(r.json())
            out_message = '-----XYBot新闻-----\n'
            for j in res:  # 从新闻列表for
                for i in range(self.news_number):  # 从设置中获取单类新闻个数
                    dict_key = list(j.keys())
                    news_title = j[dict_key[0]][i].get('title', '❓未知❓')
                    news_type = j[dict_key[0]][i].get('tname', '❓未知❓')
                    news_source = j[dict_key[0]][i].get('source', '无😔')
                    news_description = j[dict_key[0]][i].get('digest', '无😔')
                    news_url = j[dict_key[0]][i].get('url', '无😔')

                    news_output = '{title}\n类型：{type}\n来源：{source}\n{description}...\n链接🔗：{url}\n----------\n'.format(
                        title=news_title, type=news_type, source=news_source, description=news_description,
                        url=news_url)  # 创建信息
                    out_message += news_output  # 加入最后输出字符串

            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)  # 发送

        except Exception as error:  # 错误处理
            out_message = '出现错误！⚠️{error}'.format(error=error)
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)

    def get_contact_list_handler(self, recv):  # 获取机器人通讯录
        if recv['id1'] in self.admin_list:  # 判断操作人是否在管理员列表内
            heading = ['名字', '类型', '微信号(机器人用)', '微信号(加好友用)']

            chart = PrettyTable(heading)  # 创建表格

            data = self.bot.get_contact_list()  # 获取机器人通讯录
            data = data['content']

            for i in data:  # 在通讯录数据中for
                name = i['name']  # 获取昵称
                wxcode = i['wxcode']  # 获取微信号(机器人用)
                wxid = i['wxid']  # 获取微信号(加好友用)
                if wxid[:5] == 'wxid_':  # 判断是好友 群 还是其他（如文件传输助手）
                    id_type = '好友'
                elif wxid[-9:] == '@chatroom':
                    id_type = '群'
                else:
                    id_type = '其他'
                chart.add_row([name, id_type, wxid, wxcode])  # 加入表格

            chart.align = 'l'
            # 不传直接发微信是因为微信一行实在太少了，不同设备还不一样，用pywxdll发excel文件会报错
            json_data = json.dumps({"content": chart.get_string()})  # 转成json格式 用于发到api
            url = self.information_post_url + '/texts'  # 创建url
            headers = {"Content-Type": "application/json",
                       "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"}
            reqeust = requests.post(url, data=json_data, headers=headers).json()  # 发送到api
            fetch_code = reqeust['fetch_code']  # 从api获取提取码
            date_expire = reqeust['date_expire']  # 从api获取过期时间

            fetch_link = '{url}/r/{code}'.format(url=self.information_post_url, code=fetch_code)  # 创建获取链接
            out_message = '🤖️机器人的通讯录：\n{fetch_link}\n过期时间：{date_expire}'.format(fetch_link=fetch_link,
                                                                                           date_expire=date_expire)  # 组建输出信息

            self.bot.send_txt_msg(recv['wxid'], out_message)
            logger.info(
                '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))  # 发送
        else:  # 用户不是管理员
            out_message = '❌你配用这个指令吗？'
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)

    def get_chatroom_memberlist_handler(self, recv):  # 获取群成员列表
        if recv['id1'] in self.admin_list:  # 判断操作元是否是管理员
            heading = ['名字', 'wxid']
            chart = PrettyTable(heading)  # 创建列表

            data = self.bot.get_chatroom_memberlist(recv['wxid'])  # 获取操作所在群的成员列表
            data = data['content']

            for i in data:  # for循环获得的数据
                if i['room_id'] == recv['wxid']:  # 如果群号相同
                    for j in i['member']:  # for循环成员列表
                        wxid = j
                        name = self.bot.get_chatroom_nick(recv['wxid'], j)['content']['nick']  # 获取成员昵称
                        chart.add_row([name, wxid])  # 加入表格中

            chart.align = 'l'
            # 不传直接发微信是因为微信一行实在太少了，不同设备还不一样，用pywxdll发excel文件会报错
            json_data = json.dumps({"content": chart.get_string()})  # 转成json格式 用于发到api
            url = self.information_post_url + '/texts'  # 组建url
            headers = {"Content-Type": "application/json",
                       "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"}
            reqeust = requests.post(url, data=json_data, headers=headers).json()  # 向api发送数据
            fetch_code = reqeust['fetch_code']  # 从api获取提取码
            date_expire = reqeust['date_expire']  # 从api获取过期时间

            fetch_link = '{url}/r/{code}'.format(url=self.information_post_url, code=fetch_code)  # 组建提取链接
            out_message = '🤖️本群聊的群员列表：\n{fetch_link}\n过期时间：{date_expire}'.format(fetch_link=fetch_link,
                                                                                             date_expire=date_expire)  # 组建输出信息
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)  # 发送

        else:  # 操作人不是管理员
            out_message = '❌你配用这个指令吗？'
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)

    def schudle_antiautolog_handler(self):  # 防微信自动退出登录
        out_message = '防微信自动退出登录[{num}]'.format(num=random.randint(1, 9999))  # 组建信息
        logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message,
                                                                      wxid="filehelper"))  # 直接发到文件传输助手，这样就不用单独键个群辣
        self.bot.send_txt_msg("filehelper", out_message)  # 发送
