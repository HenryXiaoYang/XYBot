import json
import time

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


# 发送txt消息到个人或群 wxid为用户id或群id content为发送内容  Send txt message to a wxid(perosnal or group)
def json_send_txt_msg(wxid, content: str):
    qs = {
        'id': _getid(),
        'type': TXT_MSG,
        'roomid': 'null',
        'wxid': wxid,
        'content': content,
        'nickname': 'null',
        'ext': 'null'
    }
    return json.dumps(qs)


# 发送图片信息 wxid为用户id或群id path为发送图片的路径（建议用绝对路径） Send picture to wxid(perosnal or group)
def json_send_pic_msg(wxid, path: str):
    qs = {
        'id': _getid(),
        'type': PIC_MSG,
        'wxid': wxid,
        'roomid': 'null',
        'content': path,
        'nickname': "null",
        'ext': 'null'
    }
    s = json.dumps(qs)
    return s


# 发送@信息 roomid为群id wxid为用户id nickname为@的人昵称 content为发送内容 send @ message
def json_send_at_msg(roomid, wxid, nickname: str, content: str):
    qs = {
        'id': _getid(),
        'type': AT_MSG,
        'roomid': roomid,
        'wxid': wxid,
        'content': content,
        'nickname': nickname,
        'ext': 'null'
    }
    s = json.dumps(qs)
    return s


# 发送文件 wxid为用户id或者群id path为文件的路径 send attachment to chat or group
def json_send_attach_msg(wxid, path):
    qs = {
        'id': _getid(),
        'type': ATTATCH_FILE,
        'wxid': wxid,
        'roomid': 'null',
        'content': path,
        'nickname': "null",
        'ext': 'null'
    }

    s = json.dumps(qs)
    return s


######## 获取信息 ########

# 获取唯一id
def _getid():
    return time.strftime("%Y%m%d%H%M%S", time.localtime())


def json_heartbeat(h):
    return h


# 获取账号信息 wxid为用户id get other user's information
def json_get_personal_detail(wxid):
    qs = {
        'id': _getid(),
        'type': PERSONAL_DETAIL,
        'content': 'op:personal detail',
        'wxid': wxid,
    }
    return json.dumps(qs)


# 获取登陆的账号信息 和get_personal_detail不同于get_personal_detail是获取其他用户的 get 's imformation
def json_get_personal_info():
    qs = {
        'id': _getid(),
        'type': PERSONAL_INFO,
        'content': 'op:personal info',
        'wxid': 'ROOT',
    }
    return json.dumps(qs)


# 获取微信通讯录用户名字和wxid get wechat address list username and wxid
def json_get_contact_list():
    qs = {
        'id': _getid(),
        'type': USER_LIST,
        'content': 'user list',
        'wxid': 'null',
    }
    return json.dumps(qs)


# 获取群聊中用户昵称 wxid为群中要获取的用户id roomid为群id  get group's user's nickname
def json_get_chatroom_nick(roomid='null', wxid='ROOT'):
    if not roomid:
        roomid = 'null'
    if wxid == 'null' and roomid == 'null':
        raise ValueError("wxid和roomid不能同时为'null'")
    qs = {
        'id': _getid(),
        'type': CHATROOM_MEMBER_NICK,
        'roomid': roomid,
        'wxid': wxid,
    }
    return json.dumps(qs)


def json_get_user_nick(wxid):
    return json_get_chatroom_nick(wxid=wxid)


# 获取群聊中用户列表 wxid为群id
def json_get_chatroom_memberlist(roomid='null'):
    qs = {
        'id': _getid(),
        'type': CHATROOM_MEMBER,
        'wxid': 'null',
        'roomid': roomid,
        'content': 'op:list member',
    }
    return json.dumps(qs)


######## 其他 ########
def json_destroy_all():
    qs = {
        'id': _getid(),
        'type': DESTROY_ALL,
        'content': 'none',
        'wxid': 'node',
    }
    return json.dumps(qs)
