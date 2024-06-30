import json


# 发送txt消息到个人或群 wxid为用户id或群id content为发送内容  Send txt message to a wxid(perosnal or group)


def jsonIsLoggedIn():
    para = {
    }
    return json.dumps(para)


def jsonGetLoggedInAccountInfo():
    para = {
    }
    return json.dumps(para)


def jsonSendTextMsg(wxid: str, msg: str):
    para = {
        "wxid": wxid,
        "msg": msg
    }
    return json.dumps(para)


def jsonSendImageMsg(wxid: str, imagePath: str):
    para = {
        "wxid": wxid,
        "imagePath": imagePath
    }
    return json.dumps(para)


def jsonSendFileMsg(wxid: str, filePath: str):
    para = {
        "wxid": wxid,
        "filePath": filePath
    }
    return json.dumps(para)


def jsonStartHookMsg(port: int, ip: str, url: str, timeout: int, enableHttp: bool):
    para = {
        "port": str(port),
        "ip": ip,
        "url": url,
        "timeout": str(timeout),
        "enableHttp": str(int(enableHttp))
    }
    return json.dumps(para)


def jsonStopHookMsg():
    para = {}
    return json.dumps(para)


def jsonGetContactList():
    para = {}
    return json.dumps(para)


def jsonGetDBInfo():
    para = {}
    return json.dumps(para)


def jsonExecSql(dbHandle: int, sql: str):
    para = {
        "dbHandle": dbHandle,
        "sql": sql
    }
    return json.dumps(para)


def jsonGetChatRoomDetailInfo(chatRoomId: str):
    para = {
        "chatRoomId": chatRoomId
    }
    return json.dumps(para)


def jsonAddMemberToChatRoom(chatRoomId: str, wxids: list):
    para = {
        "chatRoomId": chatRoomId,
        "memberIds": ','.join(wxids)
    }
    return json.dumps(para)


def jsonModifyNickname(chatRoomId: str, wxid: str, nickName: str):
    para = {
        "chatRoomId": chatRoomId,
        "wxid": wxid,
        "nickName": nickName
    }
    return json.dumps(para)


def jsonDelMemberFromChatRoom(chatRoomId: str, wxids: list):
    para = {
        "chatRoomId": chatRoomId,
        "memberIds": ','.join(wxids)
    }
    return json.dumps(para)


def jsonGetMemberFromChatRoom(chatRoomId: str):
    para = {
        "chatRoomId": chatRoomId
    }
    return json.dumps(para)


def jsonTopMsg(msgId: str):
    para = {
        "msgId": msgId
    }
    return json.dumps(para)


def jsonRemoveTopMsg(msgId: str, chatRoomId: str):
    para = {
        "msgId": msgId,
        "chatRoomId": chatRoomId
    }
    return json.dumps(para)


def jsonInviteMemberToChatRoom(chatRoomId: str, wxids: list):
    para = {
        "chatRoomId": chatRoomId,
        "memberIds": ','.join(wxids)
    }
    return json.dumps(para)


def jsonHookLog():
    para = {}
    return json.dumps(para)


def jsonUnhookLog():
    para = {}
    return json.dumps(para)


def jsonCreateChatroom(wxids: list):
    para = {
        "memberIds": ','.join(wxids)
    }
    return json.dumps(para)


def jsonQuitChatroom(chatRoomId: str):
    para = {
        "chatRoomId": chatRoomId
    }
    return json.dumps(para)


def jsonForwardMsg(wxid: str, msgId: str):
    para = {
        "wxid": wxid,
        "msgId": msgId
    }
    return json.dumps(para)


def jsonGetSNSFirstPage():
    para = {}
    return json.dumps(para)


def jsonGetSNSNextPage(snsId: int):
    para = {
        "snsId": snsId
    }
    return json.dumps(para)


def jsonAddFavFromMsg(msgId: str):
    para = {
        "msgId": msgId
    }
    return json.dumps(para)


def jsonAddFavFromImage(wxid: str, imagePath: str):
    para = {
        "wxid": wxid,
        "imagePath": imagePath
    }
    return json.dumps(para)


def jsonSendAtMsg(chatRoomId: str, msg: str, wxids: list):
    para = {
        "chatRoomId": chatRoomId,
        "msg": msg,
        "wxids": ','.join(wxids)
    }
    return json.dumps(para)


def jsonGetContactProfile(wxid: str):
    para = {
        "wxid": wxid
    }
    return json.dumps(para)


def jsonSendPublicMsg(wxid: str, appName: str, userName: str, title: str, url: str, thumbUrl: str, digest: str):
    para = {
        "wxid": wxid,
        "appName": appName,
        "userName": userName,
        "title": title,
        "url": url,
        "thumbUrl": thumbUrl,
        "digest": digest
    }
    return json.dumps(para)


def jsonForwardPublicMsgByMsgId(wxid: str, msgId: str):
    para = {
        "wxid": wxid,
        "msgId": msgId
    }
    return json.dumps(para)


def jsonDownloadAttach(msgId: str):
    para = {
        "msgId": msgId,
    }
    return json.dumps(para)


def jsonDecodeImage(filePath: str, storeDir: str):
    para = {
        "filePath": filePath,
        "storeDir": storeDir
    }
    return json.dumps(para)


def jsonGetVoiceByMsgId(msgId: str, storeDir: str):
    para = {
        "msgId": msgId,
        "storeDir": storeDir
    }
    return json.dumps(para)


def jsonSendCustomEmotion(wxid: str, filePath: str):
    para = {
        "wxid": wxid,
        "filePath": filePath
    }
    return json.dumps(para)


def jsonSendApplet(wxid: str, waidConcat: str, appletWxid: str, jsonParam: str, headImgUrl: str, mainImg: str,
                   indexPage: str):
    para = {
        "wxid": wxid,
        "waidConcat": waidConcat,
        "appletWxid": appletWxid,
        "jsonParam": jsonParam,
        "headImgUrl": headImgUrl,
        "mainImg": mainImg,
        "indexPage": indexPage
    }
    return json.dumps(para)


def jsonSendPatMsg(wxid: str, patter: str):
    para = {
        "wxid": wxid,
        "receiver": patter
    }
    return json.dumps(para)


def jsonOCR(imagePath: str):
    para = {
        "imagePath": imagePath
    }
    return json.dumps(para)
