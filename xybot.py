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

        self.ip = config['ip']
        self.port = config['port']

        self.command_prefix = config['command_prefix']

        self.menu_key = config['menu_key']
        self.main_menu = config['main_menu']
        self.menus = config['menus']

        self.random_pic_link_key = config['random_pic_link_key']
        self.random_pic_link_url = config['random_pic_link_url']

        self.random_pic_key = config['random_pic_key']
        self.random_pic_url = config['random_pic_url']

        self.signin_key = config['signin_key']
        self.query_points_key = config['query_points_key']
        self.points_leaderboard_key = config['points_leaderboard_key']

        self.gpt_key = config['gpt_key']
        self.openai_api_base = config['openai_api_base']
        self.openai_api_key = config['openai_api_key']
        self.gpt_version = config['gpt_version']
        self.gpt_point_price = config['gpt_point_price']

        self.admin_list = config['admins']

        self.admin_whitelist_key = config['admin_whitelist']
        self.admin_points_key = config['admin_points']
        self.admin_signin_reset_key = config['admin_signin_reset']

        self.weather_key = config['weather_key']
        self.weather_api = config['weather_api']
        self.weather_appid = config['weather_appid']
        self.weather_appsecret = config['weather_appsecret']

        self.news_key = config['news_key']
        self.news_urls = config['news_urls']
        self.news_number = config['news_number']

        self.information_post_url = config['information_post_url']

        self.get_contact_list_key = config['get_contact_list_key']

        self.get_chatroom_memberlist_key = config['get_chatroom_memberlist_key']

        self.antoautolog_group = config['antiautolog_group']

        self.db = database.BotDatabase()

        self.bot = pywxdll.Pywxdll(self.ip, self.port)
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
                elif key in self.get_contact_list_key: #获取机器人通讯录
                    self.get_contact_list_handler(recv)
                elif key in self.get_chatroom_memberlist_key: #获取当前群成员列表
                    self.get_chatroom_memberlist_handler(recv)
                else:
                    self.bot.send_txt_msg(recv['wxid'], '该指令不存在！')
            else:
                if recv['id1'] == '':
                    recv['id1'] = recv['wxid'] #如果id1(朋友是空，群是发送人)是空，则id1为recv（即发送人）
                if key in self.menu_key:  # 菜单
                    self.menu_handler(recv)
                elif key in self.random_pic_key:  # 随机图图
                    self.random_pic_handler(recv)
                elif key in self.random_pic_link_key: # 随机链接
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
                elif key in self.get_contact_list_key: # 获取机器人通讯录
                    self.get_contact_list_handler(recv)
                elif key in self.get_chatroom_memberlist_key: # 获取微信群成员列表
                    self.get_chatroom_memberlist_handler(recv)
                else:
                    self.bot.send_txt_msg(recv['wxid'], '该指令不存在！')

    def menu_handler(self, recv):  # 菜单
        if len(recv['content']) == 1:  # 如果命令列表长度为1，那就代表请求主菜单
            self.bot.send_txt_msg(recv['wxid'], self.main_menu)
        elif recv['content'][1] in self.menus.keys():  # 长度不为1，发送以参数为键菜地内容为值的字典
            out_message = self.menus[recv['content'][1]]
            logger.info('[发送信息]' + out_message + ' | [发送到]' + recv['wxid'])
            self.bot.send_txt_msg(recv['wxid'], self.menus[recv['content'][1]])
        else:
            out_message = '找不到此菜单!⚠️'
            logger.info('[发送信息]' + out_message + ' | [发送到]' + recv['wxid'])
            self.bot.send_txt_msg(recv['wxid'], out_message)

    def random_pic_handler(self, recv):
        path = 'pic_cache/picture.png'
        with open(path, 'wb') as f:
            r = requests.get(self.random_pic_url)
            f.write(r.content)
            f.close()
        logger.info('[发送信息](随机图图图片) | [发送到]' + recv['wxid'])
        self.bot.send_pic_msg(recv['wxid'], os.path.abspath(path))

    def random_pic_link_handler(self, recv):
        r = requests.get(self.random_pic_link_url, timeout=5000)
        r.encoding = 'utf-8'
        r = r.json()
        url_list = r['pics']
        out_message = '-----XYBot-----\n❓❓❓\n'
        for i in range(1, len(url_list) + 1):
            out_message += '❓{num}：{url}\n'.format(num=i, url=url_list[i - 1])
        logger.info('[发送信息]' + out_message + ' | [发送到]' + recv['wxid'])
        self.bot.send_txt_msg(recv['wxid'], out_message)

    def bot_test_handler(self, recv):
        logger.info('[发送信息]Bot running 😊| [发送到]' + recv['wxid'])
        self.bot.send_txt_msg(recv['wxid'], 'Bot running')

    def sign_in_handler(self, recv):
        signin_points = random.randint(3, 20)
        signstat = self.db.get_stat(recv['id1'])
        nickname = self.bot.get_chatroom_nick(recv['wxid'], recv['id1'])['content']['nick']
        if signstat == 0:
            self.db.add_points(recv['id1'], signin_points)
            self.db.set_stat(recv['id1'], 1)
            out_message = '签到成功！你领到了{points}个积分！✅'.format(points=signin_points)
            logger.info('[发送信息]' + out_message + ' | [发送到]' + recv['wxid'])
            self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, out_message)
        else:
            logger.info('[发送信息] 你今天已经签到过了！❌| [发送到]' + recv['wxid'])
            self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, '你今天已经签到过了！')

    def query_points_handler(self, recv):
        nickname = self.bot.get_chatroom_nick(recv['wxid'], recv['id1'])['content']['nick']
        out_message = '你有{}点积分！👍'.format(self.db.get_points(recv['id1']))
        logger.info('[发送信息]' + out_message, ' | [发送到]' + recv['wxid'])
        self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, out_message)

    def points_leaderboard_handler(self, recv):  # 积分榜处理
        data = self.db.get_highest_points(10)
        out_message = "-----XYBot积分排行榜-----"
        rank = 1
        for i in data:
            nickname_req = self.bot.get_chatroom_nick(recv['wxid'], i[0])
            nickname = nickname_req['content']['nick']
            if nickname != nickname_req['content']['wxid']:
                out_message += "\n{rank}. {nickname} {points}分 👍".format(rank=rank, nickname=nickname,
                                                                          points=str(i[1]))
                rank += 1
        logger.info('[发送信息]' + out_message + ' | [发送到]' + recv['wxid'])
        self.bot.send_txt_msg(recv['wxid'], out_message)

    def chatgpt(self, message, recv):  # ChatGPT请求
        openai.api_key = self.openai_api_key
        openai.api_base = self.openai_api_base
        completion = ''
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
        nickname = self.bot.get_chatroom_nick(recv['wxid'], recv['id1'])['content']['nick']
        if len(recv['content']) >= 2:
            message = '已收到指令，处理中，请勿重复发送指令！👍'
            self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, message)
            if self.db.get_whitelist(recv['id1']) == 1:
                message = ''
                for i in recv['content'][1:]: message = message + str(i) + ' '
                out_message = "\n-----XYBot-----\n因为你在白名单内，所以没扣除积分！👍\nChatGPT回答：\n{res}".format(
                    res=self.chatgpt(message, recv))
                logger.info('[发送信息]' + out_message + ' | [发送到]' + recv['wxid'])
                self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, out_message)
            elif self.db.get_points(recv['id1']) >= self.gpt_point_price:
                message = ''
                for i in recv['content'][1:]: message = message + str(i) + ' '
                self.db.minus_points(recv['id1'], self.gpt_point_price)
                out_message = "\n-----XYBot-----\n已扣除{gpt_price}点积分，还剩{points_left}点积分👍\nChatGPT回答：\n{res}".format(
                    gpt_price=self.gpt_point_price, points_left=self.db.get_points(recv['id1']),
                    res=self.chatgpt(message, recv))
                self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, out_message)
            else:
                self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname,
                                     "积分不足！需要{}点！👎".format(self.gpt_point_price))
        else:
            out_message = '参数错误！⚠️'
            logger.info('[发送信息]' + out_message + ' | [发送到]' + recv['wxid'])
            self.bot.send_at_msg(recv['wxid'], recv['id1'], nickname, out_message)

    def friend_chatgpt_handler(self, recv):
        if len(recv['content']) >= 2:
            message = '已收到指令，处理中，请勿重复发送指令！👍'
            self.bot.send_txt_msg(recv['wxid'], message)
            if self.db.get_whitelist(recv['wxid']) == 1:
                message = ''
                for i in recv['content'][1:]: message = message + str(i) + ' '
                out_message = "-----XYBot-----\n因为你在白名单内，所以没扣除积分！👍\nChatGPT回答：\n{res}".format(
                    res=self.chatgpt(message, recv))
                logger.info('[发送信息]' + out_message + ' | [发送到]' + recv['wxid'])
                self.bot.send_txt_msg(recv['wxid'], out_message)
            elif self.db.get_points(recv['wxid']) >= self.gpt_point_price:
                message = ''
                for i in recv['content'][1:]: message = message + str(i) + ' '
                self.db.minus_points(recv['wxid'], self.gpt_point_price)
                out_message = "-----XYBot-----\n已扣除{gpt_price}点积分，还剩{points_left}点积分👍\nChatGPT回答：\n{res}".format(
                    gpt_price=self.gpt_point_price, points_left=self.db.get_points(recv['wxid']),
                    res=self.chatgpt(message, recv))
                logger.info('[发送信息]' + out_message + ' | [发送到]' + recv['wxid'])
                self.bot.send_txt_msg(recv['wxid'], out_message)
            else:
                out_message = "积分不足！👎需要{}点！".format(self.gpt_point_price)
                logger.info('[发送信息]' + out_message + ' | [发送到]' + recv['wxid'])
                self.bot.send_txt_msg(recv['wxid'], out_message)
        else:
            out_message = '参数错误！⚠️'
            logger.info('[发送信息]' + out_message + ' | [发送到]' + recv['wxid'])
            self.bot.send_txt_msg(recv['wxid'], out_message)

    def admin_whitelist_handler(self, recv):  # 管理白名单处理
        wxid = recv['content'][1]
        action = recv['content'][2]
        if recv['id1'] in self.admin_list:
            if action == '加入':
                self.db.set_whitelist(wxid, 1)
            elif action == '删除':
                self.db.set_whitelist(wxid, 0)
            out_message = '成功修改{}的白名单！😊'.format(wxid)
            logger.info('[发送信息]' + out_message + ' | [发送到]' + recv['wxid'])
            self.bot.send_txt_msg(recv['wxid'], out_message)
        else:
            logger.info('[发送信息]你配用这个指令吗？ | [发送到]' + recv['wxid'])
            self.bot.send_txt_msg(recv['wxid'], '❌你配用这个指令吗？')

    def admin_points_handler(self, recv):  # 管理积分处理
        wxid = recv['content'][1]
        action = recv['content'][2]
        if recv['id1'] in self.admin_list:
            if len(recv['content']) == 3:
                self.db.set_points(wxid, int(action))
            elif action == '加':
                self.db.add_points(wxid, int(recv['content'][3]))
            elif action == '减':
                self.db.minus_points(wxid, int(recv['content'][3]))
            else:
                self.bot.send_txt_msg(recv['wxid'], '参数错误！{action}'.format(action=action))
                logger.debug('管理积分参数错误！⚠️{action}'.format(action=action))
                return

            total_points = self.db.get_points(wxid)
            fmsg = '😊成功给{wxid}{action}了{points}点积分！他现在有{total}点积分！'
            out_message = fmsg.format(wxid=wxid, action=action, points=recv['content'][3], total=total_points)
            logger.info('[发送信息]' + out_message + ' | [发送到]' + recv['wxid'])
            self.bot.send_txt_msg(recv['wxid'], out_message)
        else:
            logger.info('[发送信息]❌你配用这个指令吗？ ｜ [发送到]' + recv['wxid'])
            self.bot.send_txt_msg(recv['wxid'], '❌你配用这个指令吗？')

    def admin_signin_reset(self, recv):
        if recv['id1'] in self.admin_list:
            self.db.reset_stat()
            out_message = '😊成功重置签到状态！'
            logger.info('[发送信息]' + out_message + ' | [发送到]' + recv['wxid'])
            self.bot.send_txt_msg(recv['wxid'], out_message)
        else:
            logger.info('[发送信息]❌你配用这个指令吗？ ｜ [发送到]' + recv['wxid'])
            self.bot.send_txt_msg(recv['wxid'], '❌你配用这个指令吗？')

    def weather_handler(self, recv):
        city = recv['content'][1]
        url = "{api}?appid={appid}&appsecret={appsecret}&unescape=1&city={city}".format(api=self.weather_api,
                                                                                        appid=self.weather_appid,
                                                                                        appsecret=self.weather_appsecret,
                                                                                        city=city)
        try:
            r = requests.get(url, timeout=5000)
            r.encoding = 'utf-8'
            res = r.json()
            out_message = '-----XYBot-----\n城市🌆：{city}\n天气☁️：{weather}\n实时温度🌡️：{temp}°\n白天温度🌡：{temp_day}°\n夜晚温度🌡：{temp_night}°\n空气质量🌬：{air_quality}\n空气湿度💦：{air_humidity}\n风向🌬：{wind_speed}{wind_dir}\n更新时间⌚：{update_time}'.format(
                city=res['city'], weather=res['wea'], temp=res['tem'], temp_day=res['tem_day'],
                temp_night=res['tem_night'], air_quality=res['air'], air_humidity=res['humidity'], wind_dir=res['win'],
                wind_speed=res['win_speed'], update_time=res['update_time'])
            logger.info('[发送信息]' + out_message + ' | [发送到]' + recv['wxid'])
            self.bot.send_txt_msg(recv['wxid'], out_message)
        except Exception as error:
            out_message = '出现错误！⚠️{error}'.format(error=error)
            logger.info('[发送信息]' + out_message + ' | [发送到]' + recv['wxid'])
            self.bot.send_txt_msg(recv['wxid'], out_message)

    def news_handler(self, recv):
        try:
            res = []
            for i in self.news_urls:
                r = requests.get(i, timeout=5000)
                r.encoding = 'utf-8'
                res.append(r.json())
            out_message = '-----XYBot新闻-----\n'
            for j in res:
                for i in range(self.news_number):
                    dict_key = list(j.keys())
                    news_title = j[dict_key[0]][i].get('title', '❓未知❓')
                    news_type = j[dict_key[0]][i].get('tname', '❓未知❓')
                    news_source = j[dict_key[0]][i].get('source', '无😔')
                    news_description = j[dict_key[0]][i].get('digest', '无😔')
                    news_url = j[dict_key[0]][i].get('url', '无😔')

                    news_output = '{title}\n类型：{type}\n来源：{source}\n{description}\n链接🔗：{url}\n----------\n'.format(
                        title=news_title, type=news_type, source=news_source, description=news_description,
                        url=news_url)
                    out_message += news_output

            logger.info('[发送信息]' + out_message + ' | [发送到]' + recv['wxid'])
            self.bot.send_txt_msg(recv['wxid'], out_message)

        except Exception as error:
            out_message = '出现错误！⚠️{error}'.format(error=error)
            logger.info('[发送信息]' + out_message + ' | [发送到]' + recv['wxid'])
            self.bot.send_txt_msg(recv['wxid'], out_message)

    def get_contact_list_handler(self, recv):
        if recv['id1'] in self.admin_list:
            heading = ['名字', '类型', '微信号(机器人用)', '微信号(加好友用)']

            chart = PrettyTable(heading)

            data = self.bot.get_contact_list()
            data = data['content']

            for i in data:
                name = i['name']
                wxcode = i['wxcode']
                wxid = i['wxid']
                if wxid[:5] == 'wxid_':
                    type = '好友'
                elif wxid[-9:] == '@chatroom':
                    type = '群'
                else:
                    type = '其他'
                chart.add_row([name, type, wxid, wxcode])

            chart.align = 'l'
            json_data = json.dumps({"content": chart.get_string()})
            url = self.information_post_url + '/texts'
            headers = {"Content-Type": "application/json",
                       "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"}
            reqeust = requests.post(url, data=json_data, headers=headers).json()
            fetch_code = reqeust['fetch_code']
            date_expire = reqeust['date_expire']

            fetch_link = '{url}/r/{code}'.format(url=self.information_post_url, code=fetch_code)
            out_message = '🤖️机器人的通讯录：\n{fetch_link}\n过期时间：{date_expire}'.format(fetch_link=fetch_link,
                                                                                                 date_expire=date_expire)

            self.bot.send_txt_msg(recv['wxid'], out_message)
            logger.info('[发送信息]' + out_message + ' | [发送到]' + recv['wxid'])
        else:
            logger.info('[发送信息]❌你配用这个指令吗？ ｜ [发送到]' + recv['wxid'])
            self.bot.send_txt_msg(recv['wxid'], '❌你配用这个指令吗？')

    def get_chatroom_memberlist_handler(self, recv):
        if recv['id1'] in self.admin_list:
            heading = ['名字', 'wxid']
            chart = PrettyTable(heading)

            data = self.bot.get_chatroom_memberlist(recv['wxid'])
            data = data['content']

            for i in data:
                if i['room_id'] == recv['wxid']:
                    for j in i['member']:
                        wxid = j
                        name = self.bot.get_chatroom_nick(recv['wxid'], j)['content']['nick']
                        chart.add_row([name, wxid])

            chart.align = 'l'
            # 不传直接发微信是因为微信一行实在太少了，不同设备还不一样，用pywxdll发excel文件会报错
            json_data = json.dumps({"content": chart.get_string()})
            url = self.information_post_url + '/texts'
            headers = {"Content-Type": "application/json",
                       "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"}
            reqeust = requests.post(url, data=json_data, headers=headers).json()
            fetch_code = reqeust['fetch_code']
            date_expire = reqeust['date_expire']

            fetch_link = '{url}/r/{code}'.format(url=self.information_post_url, code=fetch_code)
            out_message = '🤖️本群聊的群员列表：\n{fetch_link}\n过期时间：{date_expire}'.format(fetch_link=fetch_link,
                                                                                             date_expire=date_expire)

            self.bot.send_txt_msg(recv['wxid'], out_message)
            logger.info('[发送信息]' + out_message + ' | [发送到]' + recv['wxid'])
        else:
            logger.info('[发送信息]❌你配用这个指令吗？ ｜ [发送到]' + recv['wxid'])
            self.bot.send_txt_msg(recv['wxid'], '❌你配用这个指令吗？')

    def schudle_antiautolog_handler(self):
        if self.antoautolog_group != '':
            out_message = '防微信自动退出登录[{num}]'.format(num=random.randint(1,9999))
            self.bot.send_txt_msg(self.antoautolog_group, out_message)
            logger.info('[发送信息]' + out_message + ' | [发送到]' + self.antoautolog_group)
        else:
            logger.debug('设置中未填写防微信自动退出登录群号')