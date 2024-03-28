import threading

import requests
import websocket

from utils.web_api_data import WebApiData
from .pywxdll_json import *

HEART_BEAT = 5005
RECV_TXT_MSG = 1
RECV_PIC_MSG = 3
NEW_FRIEND_REQUEST = 37
RECV_TXT_CITE_MSG = 49
PIC_MSG = 500
AT_MSG = 550
TXT_MSG = 555
USER_LIST = 5000
GET_USER_LIST_SUCCSESS = 5001
GET_USER_LIST_FAIL = 5002
ATTATCH_FILE = 5003
CHATROOM_MEMBER = 5010
CHATROOM_MEMBER_NICK = 5020
DEBUG_SWITCH = 6000
PERSONAL_INFO = 6500
PERSONAL_DETAIL = 6550
DESTROY_ALL = 9999
JOIN_ROOM = 10000


class Pywxdll:
    def __init__(self, ip='127.0.0.1', port=5555):  # 微信hook服务器的ip地址和端口 The ip and port for wechat hook server
        '''
        :param ip:
        :param port:
        '''
        self.ip = ip
        self.port = port
        self._ws_url = f'ws://{ip}:{port}'  # websocket url
        self.msg_list = []

        self._web_api_data = WebApiData()

    def _thread_start(self):  # 监听hook The thread for listeing
        websocket.enableTrace(False)  # 开启调试？
        ws = websocket.WebSocketApp(
            self._ws_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        ws.run_forever()

    def start(self):  # 开始监听 Start listening for incoming message
        '''
        开始监听微信消息 Start listening for incoming message
        :return:
        '''
        wxt = threading.Thread(target=self._thread_start)
        wxt.daemon = True
        wxt.start()

    def _on_open(self, ws):  # For websocket
        pass

    def _on_message(self, ws, message):  # For websocket
        recieve = json.loads(message)
        r_type = recieve['type']
        if r_type == 5005:
            pass
        elif r_type == 1 or r_type == 3 or r_type == 49:
            self.msg_list.append(self._recv_txt_handle(recieve))

    def _on_error(self, ws, error):  # For websocket
        raise error

    def _on_close(self, ws):  # For websocket
        pass

    ######## Send ########
    def _send_http(self, uri, data):
        if isinstance(data, str) or isinstance(data, bytes):
            data = json.loads(data)
        base_data = {
            'id': self._getid(),
            'type': 'null',
            'roomid': 'null',
            'wxid': 'null',
            'content': 'null',
            'nickname': 'null',
            'ext': 'null',
        }
        base_data.update(data)
        url = f'http://{self.ip}:{self.port}/{uri}'

        rsp = requests.post(url, json={'para': base_data})

        rsp = rsp.json()
        if 'content' in rsp and isinstance(rsp['content'], str):
            try:
                rsp['content'] = json.loads(rsp['content'])
            except:
                pass
        return rsp

    def send_txt_msg(self, wxid: str, content: str):
        '''
        发送txt消息到朋友或群 Send txt message to a friend or chatroom
        :param wxid: wxid(新用户的wxid以wxid_开头 老用户他们可能修改过 现在改不了)或者群号(以@chatroom结尾) wechatid(start with wxid_) or groupchatid(end with@chatroom)
        :param content: 要发送的文本 content to send
        :return: Dictionary
        '''
        uri = '/api/sendtxtmsg'
        self._web_api_data.update_data('sent_message_count', self._web_api_data.get_data()['sent_message_count'] + 1)
        return self._send_http(uri, json_send_txt_msg(wxid, content))

    def send_pic_msg(self, wxid: str, path: str):
        '''
        发送图片信息发送txt消息到朋友或群 Send picture to a friend or chatroom
        :param wxid: wxid(新用户的wxid以wxid_开头 老用户他们可能修改过 现在改不了)或者群号(以@chatroom结尾) wechatid(start with wxid_) or groupchatid(end with@chatroom)
        :param path: 图片路径 path to picture
        :return:
        '''
        uri = '/api/sendpic'
        self._web_api_data.update_data('sent_message_count', self._web_api_data.get_data()['sent_message_count'] + 1)
        return self._send_http(uri, json_send_pic_msg(wxid, path))

    def send_at_msg(self, roomid: str, wxid: str, nickname: str, content: str):
        '''
        发送@信息到群  send @ message to chatroom
        :param roomid: 群号(以@chatroom结尾) groupchatid(end with@chatroom)
        :param wxid: 要@的人的wxid(新用户的wxid以wxid_开头 老用户他们可能修改过 现在改不了) wechatid(start with wxid_) of person you want to @
        :param nickname: 要@的人的昵称，可随意修改 nickname of person you want to @
        :param content: 要发送的文本 content to send
        :return:
        '''
        uri = '/api/sendatmsg'
        self._web_api_data.update_data('sent_message_count', self._web_api_data.get_data()['sent_message_count'] + 1)
        return self._send_http(uri, json_send_at_msg(roomid, wxid, nickname, content))

    def send_attach_msg(self, wxid: str, path: str):
        '''
        发送文件到朋友或群 send attachment to friend or chatroom
        :param wxid: wxid(新用户的wxid以wxid_开头 老用户他们可能修改过 现在改不了)或者群号(以@chatroom结尾) wechatid(start with wxid_) or groupchatid(end with@chatroom)
        :param path: 文件的路径 path to file
        :return:
        '''
        uri = '/api/sendattatch'
        self._web_api_data.update_data('sent_message_count', self._web_api_data.get_data()['sent_message_count'] + 1)
        return self._send_http(uri, json_send_attach_msg(wxid, path))

    ######## 获取信息 ########

    # 获取唯一id
    def _getid(self):
        return time.strftime("%Y%m%d%H%M%S", time.localtime())

    def heartbeat(h):
        return h

    def get_personal_detail(self, wxid: str):
        '''
        获取其他账号信息 get other user's information
        :param wxid: wxid(新用户的wxid以wxid_开头 老用户他们可能修改过 现在改不了) wechatid(start with wxid_)
        :return: Dictionary
        '''
        uri = '/api/get_personal_detail'
        return self._send_http(uri, json_get_personal_detail(wxid))['content']

    def get_contact_list(self):
        '''
        获取微信通讯录用户名字和wxid get wechat address list username and wxid
        :return: Dictionary
        '''
        uri = '/api/getcontactlist'
        return self._send_http(uri, json_get_contact_list())['content']

    def get_chatroom_nickname(self, roomid: str = 'null', wxid: str = 'ROOT'):
        '''
        获取群聊中用户昵称 Get chatroom's user's nickname
        :param roomid: 群号(以@chatroom结尾) groupchatid(end with@chatroom)
        :param wxid: wxid(新用户的wxid以wxid_开头 老用户他们可能修改过 现在改不了) wechatid(start with wxid_)
        :return: Dictionary
        '''
        uri = 'api/getmembernick'
        return self._send_http(uri, json_get_chatroom_nick(roomid, wxid))['content']

    def get_user_nickname(self, wxid: str):
        '''
        获取朋友昵称 Get friend's nickname
        :param wxid: wxid(新用户的wxid以wxid_开头 老用户他们可能修改过 现在改不了) wechatid(start with wxid_)
        :return: Dictionary
        '''
        return self.get_chatroom_nickname(wxid=wxid)

    def get_chatroom_memberlist(self, roomid: str = 'null'):
        '''
        获取群聊中用户列表 Get chatroom member list
        :param roomid: 群号(以@chatroom结尾) groupchatid(end with@chatroom)
        :return: List or Dictionary
        '''
        uri = '/api/get_charroom_member_list'
        result = self._send_http(uri, json_get_chatroom_memberlist(roomid))['content']
        if roomid == 'null':
            return result
        else:
            for i in result:
                if i['room_id'] == roomid:
                    return i
            return result

    ######## 信息处理 ########

    def _recv_txt_handle(self, recieve):
        return recieve
