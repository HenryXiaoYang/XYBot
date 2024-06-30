import json


# 发送txt消息到个人或群 wxid为用户id或群id content为发送内容  Send txt message to a wxid(perosnal or group)


def json_is_logged_in():
    para = {
    }
    return json.dumps(para)


def json_get_logged_in_account_info():
    para = {
    }
    return json.dumps(para)


def json_send_text_msg(wxid: str, msg: str):
    para = {
        "wxid": wxid,
        "msg": msg
    }
    return json.dumps(para)


def json_send_image_msg(wxid: str, image_path: str):
    para = {
        "wxid": wxid,
        "imagePath": image_path
    }
    return json.dumps(para)


def json_send_file_msg(wxid: str, file_path: str):
    para = {
        "wxid": wxid,
        "filePath": file_path
    }
    return json.dumps(para)


def json_start_hook_msg(port: int, ip: str, url: str, timeout: int, enable_http: bool):
    para = {
        "port": str(port),
        "ip": ip,
        "url": url,
        "timeout": str(timeout),
        "enableHttp": str(int(enable_http))
    }
    return json.dumps(para)


def json_stop_hook_msg():
    para = {}
    return json.dumps(para)


def json_get_contact_list():
    para = {}
    return json.dumps(para)


def json_get_db_info():
    para = {}
    return json.dumps(para)


def json_exec_sql(db_handle: int, sql: str):
    para = {
        "dbHandle": db_handle,
        "sql": sql
    }
    return json.dumps(para)


def json_get_chatroom_detail_info(chatroom_id: str):
    para = {
        "chatRoomId": chatroom_id
    }
    return json.dumps(para)


def json_add_member_to_chatroom(chatroom_id: str, wxids: list):
    para = {
        "chatRoomId": chatroom_id,
        "memberIds": ','.join(wxids)
    }
    return json.dumps(para)


def json_modify_nickname(chatroom_id: str, wxid: str, nickname: str):
    para = {
        "chatRoomId": chatroom_id,
        "wxid": wxid,
        "nickName": nickname
    }
    return json.dumps(para)


def json_del_member_from_chatroom(chatroom_id: str, wxids: list):
    para = {
        "chatRoomId": chatroom_id,
        "memberIds": ','.join(wxids)
    }
    return json.dumps(para)


def json_get_member_from_chatroom(chatroom_id: str):
    para = {
        "chatRoomId": chatroom_id
    }
    return json.dumps(para)


def json_top_msg(msg_id: str):
    para = {
        "msgId": msg_id
    }
    return json.dumps(para)


def json_remove_top_msg(msg_id: str, chatroom_id: str):
    para = {
        "msgId": msg_id,
        "chatRoomId": chatroom_id
    }
    return json.dumps(para)


def json_invite_member_to_chatroom(chatroom_id: str, wxids: list):
    para = {
        "chatRoomId": chatroom_id,
        "memberIds": ','.join(wxids)
    }
    return json.dumps(para)


def json_hook_log():
    para = {}
    return json.dumps(para)


def json_unhook_log():
    para = {}
    return json.dumps(para)


def json_create_chatroom(wxids: list):
    para = {
        "memberIds": ','.join(wxids)
    }
    return json.dumps(para)


def json_quit_chatroom(chatroom_id: str):
    para = {
        "chatRoomId": chatroom_id
    }
    return json.dumps(para)


def json_forward_msg(wxid: str, msg_id: str):
    para = {
        "wxid": wxid,
        "msgId": msg_id
    }
    return json.dumps(para)


def json_get_sns_first_page():
    para = {}
    return json.dumps(para)


def json_get_sns_next_page(sns_id: int):
    para = {
        "snsId": sns_id
    }
    return json.dumps(para)


def json_add_fav_from_msg(msg_id: str):
    para = {
        "msgId": msg_id
    }
    return json.dumps(para)


def json_add_fav_from_image(wxid: str, image_path: str):
    para = {
        "wxid": wxid,
        "imagePath": image_path
    }
    return json.dumps(para)


def json_send_at_msg(chatroom_id: str, msg: str, wxids: list):
    para = {
        "chatRoomId": chatroom_id,
        "msg": msg,
        "wxids": ','.join(wxids)
    }
    return json.dumps(para)


def json_get_contact_profile(wxid: str):
    para = {
        "wxid": wxid
    }
    return json.dumps(para)


def json_send_public_msg(wxid: str, app_name: str, username: str, title: str, url: str, thumb_url: str, digest: str):
    para = {
        "wxid": wxid,
        "appName": app_name,
        "userName": username,
        "title": title,
        "url": url,
        "thumbUrl": thumb_url,
        "digest": digest
    }
    return json.dumps(para)


def json_forward_public_msg_by_msg_id(wxid: str, msg_id: str):
    para = {
        "wxid": wxid,
        "msgId": msg_id
    }
    return json.dumps(para)


def json_download_attach(msg_id: str):
    para = {
        "msgId": msg_id,
    }
    return json.dumps(para)


def json_decode_image(file_path: str, store_dir: str):
    para = {
        "filePath": file_path,
        "storeDir": store_dir
    }
    return json.dumps(para)


def json_get_voice_by_msg_id(msg_id: str, store_dir: str):
    para = {
        "msgId": msg_id,
        "storeDir": store_dir
    }
    return json.dumps(para)


def json_send_custom_emotion(wxid: str, file_path: str):
    para = {
        "wxid": wxid,
        "filePath": file_path
    }
    return json.dumps(para)


def json_send_applet(wxid: str, waid_concat: str, applet_wxid: str, json_param: str, head_img_url: str, main_img: str,
                     index_page: str):
    para = {
        "wxid": wxid,
        "waidConcat": waid_concat,
        "appletWxid": applet_wxid,
        "jsonParam": json_param,
        "headImgUrl": head_img_url,
        "mainImg": main_img,
        "indexPage": index_page
    }
    return json.dumps(para)


def json_send_pat_msg(wxid: str, patter: str):
    para = {
        "wxid": wxid,
        "receiver": patter
    }
    return json.dumps(para)


def json_ocr(image_path: str):
    para = {
        "imagePath": image_path
    }
    return json.dumps(para)
