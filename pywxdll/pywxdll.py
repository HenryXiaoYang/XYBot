import ctypes
import os
import platform
import subprocess
import sys
import time

import requests
from loguru import logger

from utils.web_api_data import WebApiData
from .pywxdll_json import *


class Pywxdll:
    def __init__(self, ip='127.0.0.1', port=19088):  # 微信hook服务器的ip地址和端口 The ip and port for WeChat hook server
        """
        :param ip:
        :param port:
        """
        self.ip = ip
        self.port = port
        self.base_url = f"http://{ip}:{port}/api"

        self.docker_injector_path = os.path.abspath("pywxdll/Injector_Docker.exe")
        self.windows_wechat_start_path = os.path.abspath("pywxdll/StartWxAndInject_Windows.exe")
        self.windows_wechat_start_admin_script_path = "pywxdll/windows_start_wechat_and_inject_admin.py"
        self.dll_filename = "wxhelper-3.9.5.81-v11.dll"
        self.dll_path_relative = "pywxdll/wxhelper-3.9.5.81-v11.dll"
        self.dll_path_absolute = os.path.abspath("pywxdll/wxhelper-3.9.5.81-v11.dll")
        self.injection_process_name = "WeChat.exe"
        self.wechat_version_fix_path = os.path.abspath("pywxdll/fixWechatVersion.py")

        self._web_api_data = WebApiData()

    def docker_inject_dll(self):
        """
        This function is to inject the wxhelper dll into WeChat process in Docker environment
        :return: True if success, False if failed.
        """
        result = subprocess.Popen(
            f"cd ~ && wine {self.docker_injector_path} --process-name {self.injection_process_name} --inject {self.dll_filename}",
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
        # The injector has a bug that it returns Call to LoadLibraryW
        # in remote process failed even if the injection is successful.
        time.sleep(3)
        result = ''.join(result.communicate())
        logger.debug(result)
        if "LoadLibraryW" in result or "Successfully" in result:
            return True
        else:
            return False

    @staticmethod
    def _is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def windows_start_wechat_inject_and_fix_ver(self):
        """
        This function is to start WeChat and inject the wxhelper dll on Windows environment
        :return:
        """

        if not self._is_admin():
            # 需要管理员权限，这一行申请了管理员并执行了一个python脚本。python脚本注入了hook，修复了版本问题
            result = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable,
                                                         f"{self.windows_wechat_start_admin_script_path} {self.windows_wechat_start_path} {self.dll_path_absolute} {self.port} {self.wechat_version_fix_path}",
                                                         None, 1)
            time.sleep(3)  # 等待注入
            if int(result) > 32:  # 返回值大于32即成功 https://learn.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-shellexecutew
                result = True
            else:
                result = False
        else:
            result = subprocess.Popen(f"{self.windows_wechat_start_path} {self.dll_path_absolute} {self.port}",
                                      shell=True,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
            result = ''.join(result.communicate())
            logger.debug(result)
        if result:
            return True
        else:
            return False

    def fix_wechat_version(self) -> bool:
        """
        This function is to fix the WeChat version
        :return: True if success, Flase if failed.
        """
        if platform.system() == 'Windows':
            command = f"python {self.wechat_version_fix_path}"
        else:
            command = f"cd ~ && wine python {self.wechat_version_fix_path}"

        result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')

        result = ''.join(result.communicate())
        logger.debug(result)
        if 'Fix Success' in result:
            return True
        else:
            return False

    def raw_is_logged_in(self) -> dict:
        url = f"{self.base_url}/checkLogin"
        json_para = json_is_logged_in()
        response = requests.post(url, data=json_para)
        return response.json()

    def is_logged_in(self) -> bool:
        """
        Check if the WeChat is logged in or not.
        :return: A boolean, True if logged in, False if not logged in.
        """
        json_response = self.raw_is_logged_in()
        if json_response.get('code') == 1:
            return True
        else:
            return False

    def raw_get_logged_in_account_info(self):
        url = f"{self.base_url}/userInfo"
        json_para = json_get_logged_in_account_info()
        response = requests.post(url, data=json_para)
        return response.json()

    def get_logged_in_account_info(self) -> dict:
        """
        Get information of the account logged into.
        :return: A dictionary, including: wxid(string) account(string) headImage(string) city(string) country(string) \
        currentDataPath(string) dataSavePath(string) mobile(string) name(string) province(string) signature(string)
        """
        json_response = self.raw_get_logged_in_account_info()
        data = json_response.get('data')
        return data

    def raw_send_text_msg(self, wxid: str, msg: str):
        url = f"{self.base_url}/sendTextMsg"
        json_para = json_send_text_msg(wxid, msg)
        response = requests.post(url, data=json_para)
        return response.json()

    def send_text_msg(self, wxid: str, msg: str) -> bool:
        """
        Send a text message to the wxid.
        :param wxid: WeChat account identifier
        :param msg: The message needed to send
        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_send_text_msg(wxid, msg)
        if json_response.get('code') == 0 or json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_send_image_msg(self, wxid: str, image_path: str):
        url = f"{self.base_url}/sendImagesMsg"
        json_para = json_send_image_msg(wxid, image_path)
        response = requests.post(url, data=json_para)
        return response.json()

    def send_image_msg(self, wxid: str, image_path: str) -> bool:
        """
        Send a picture message to the wxid.
        :param wxid: WeChat account identifier
        :param image_path: The path of the image
        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_send_image_msg(wxid, image_path)
        if json_response.get('code') == 0 or json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_send_file_msg(self, wxid: str, file_path: str):
        url = f"{self.base_url}/sendFileMsg"
        json_para = json_send_file_msg(wxid, file_path)
        response = requests.post(url, data=json_para)
        return response.json()

    def send_file_msg(self, wxid: str, file_path: str) -> bool:
        """
        Send a file message to the wxid.
        :param wxid: WeChat account identifier
        :param file_path: The path of the file
        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_send_file_msg(wxid, file_path)
        if json_response.get('code') == 0 or json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_start_hook_msg(self, port: int, ip: str, hook_url: str = '', timeout: int = 3000,
                           enable_http: bool = False):
        url = f"{self.base_url}/hookSyncMsg"
        json_para = json_start_hook_msg(port, ip, hook_url, timeout, enable_http)
        response = requests.post(url, data=json_para)
        return response.json()

    def start_hook_msg(self, port: int, ip: str = '127.0.0.1', hook_url: str = '', timeout: int = 3000,
                       enable_http: bool = False) -> bool:
        """
        Start hooking the message and send to the tcp server
        :param port: The port of tcp server
        :param ip: The ip of tcp server
        :param hook_url: Optional, the url of the tcp server. When enableHttp is True, this is required.
        :param timeout: Optional, the timeout of sending tcp request, default is 3000ms
        :param enable_http: Optional, enable http or not, default is False
        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_start_hook_msg(port, ip, hook_url, timeout, enable_http)
        if json_response.get('code') == 0 or json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_stop_hook_msg(self):
        url = f"{self.base_url}/unhookSyncMsg"
        json_para = json_stop_hook_msg()
        response = requests.post(url, data=json_para)
        return response.json()

    def stop_hook_msg(self) -> bool:
        """
        Stop the hook server
        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_stop_hook_msg()
        if json_response.get('code') == 0:
            return True
        else:
            return False

    def raw_get_contect_list(self):
        url = f"{self.base_url}/getContactList"
        json_para = json_get_contact_list()
        response = requests.post(url, data=json_para)
        return response.json()

    def get_contact_list(self) -> list:
        """
        Get the contact list
        :return: A list of contact information
        """
        json_response = self.raw_get_contect_list()
        data = json_response.get('data')
        return data

    def raw_get_db_info(self):
        url = f"{self.base_url}/getDBInfo"
        json_para = json_get_db_info()
        response = requests.post(url, data=json_para)
        return response.json()

    def get_db_info(self) -> dict:
        """
        Gets database information and handles
        :return: Information of database. Including database name(string), handle(int), tables(list), name(string), \
        rootpage(string), sql(string), table name(string).
        """
        json_response = self.raw_get_db_info()
        data = json_response.get('data')
        return data

    def raw_exec_sql(self, db_handle: int, sql: str):
        url = f"{self.base_url}/execSql"
        json_para = json_exec_sql(db_handle, sql)
        response = requests.post(url, data=json_para)
        return response.json()

    def exec_sql(self, db_handle: int, sql: str) -> list:
        """
        Execute the sql command in WeChat database
        :param db_handle: The handle of the database
        :param sql: The sql command
        :return: The result of the sql command
        """
        json_response = self.raw_exec_sql(db_handle, sql)
        data = json_response.get('data')
        return data

    def raw_get_chatroom_detail_info(self, chatroom_id: str):
        url = f"{self.base_url}/getChatRoomDetailInfo"
        json_para = json_get_chatroom_detail_info(chatroom_id)
        response = requests.post(url, data=json_para)
        return response.json()

    def get_chatroom_detail_info(self, chatroom_id: str) -> dict:
        """
        Get chatroom details
        :param chatroom_id: Chatroom identifier.
        :return: A dictionary, including: chatRoomId(string) chatRoomName(string) notice(string) admin(int) \
        xml information(list).
        """
        json_response = self.raw_get_chatroom_detail_info(chatroom_id)
        data = json_response.get('data')
        return data

    def raw_add_member_to_chatroom(self, chatroom_id: str, wxids: list):
        url = f"{self.base_url}/addMemberToChatRoom"
        json_para = json_add_member_to_chatroom(chatroom_id, wxids)
        response = requests.post(url, data=json_para)
        return response.json()

    def add_member_to_chatroom(self, chatroom_id: str, wxids: list) -> bool:
        """
        Add members to chatroom
        :param chatroom_id: Chatroom identifier
        :param wxids: The list of wxid you want to add
        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_add_member_to_chatroom(chatroom_id, wxids)
        if json_response.get('code') == 1:
            return True
        else:
            return False

    def raw_modify_nickname(self, chatroom_id: str, wxid: str, nickname: str):
        url = f"{self.base_url}/modifyNickname"
        json_para = json_modify_nickname(chatroom_id, wxid, nickname)
        response = requests.post(url, data=json_para)
        return response.json()

    def modify_nickname(self, chatroom_id: str, wxid: str, nickname: str) -> bool:
        """
        Modify the nickname in chatroom
        :param chatroom_id: Chatroom identifier
        :param wxid: The wxid you want to modify
        :param nickname: The nickname you want to modify
        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_modify_nickname(chatroom_id, wxid, nickname)
        if json_response.get('code') == 1:
            return True
        else:
            return False

    def raw_del_member_from_chatroom(self, chatroom_id: str, wxids: list):
        url = f"{self.base_url}/delMemberFromChatRoom"
        json_para = json_del_member_from_chatroom(chatroom_id, wxids)
        response = requests.post(url, data=json_para)
        return response.json()

    def del_member_from_chatroom(self, chatroom_id: str, wxids: list) -> bool:
        """
        Delete members from chatroom
        :param chatroom_id: Chatroom identifier
        :param wxids: The list of wxid you want to delete
        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_del_member_from_chatroom(chatroom_id, wxids)
        if json_response.get('code') == 1:
            return True
        else:
            return False

    def raw_get_member_from_chatroom(self, chatroom_id: str):
        url = f"{self.base_url}/getMemberFromChatRoom"
        json_para = json_get_member_from_chatroom(chatroom_id)
        response = requests.post(url, data=json_para)
        return response.json()

    def get_member_from_chatroom(self, chatroom_id: str) -> dict:
        """
        Get members from chatroom
        :param chatroom_id: Chatroom identifier
        :return: A dictionary, including: admin(string) adminNickname(string) chatRoomId(string) \
        memberNickname(string) members(string).
        """
        json_response = self.raw_get_member_from_chatroom(chatroom_id)
        data = json_response.get('data')
        data['memberNickname'] = data.get('memberNickname').split('^G')
        data['members'] = data.get('members').split('^G')
        return data

    def raw_top_msg(self, msg_id: str):
        url = f"{self.base_url}/topMsg"
        json_para = json_top_msg(msg_id)
        response = requests.post(url, data=json_para)
        return response.json()

    def top_msg(self, msg_id: str):
        """
        Top a message in chatroom. Chatroom admin is needed
        :param msg_id: The message identifier
        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_top_msg(msg_id)
        if json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_remove_top_msg(self, msg_id: str, chatroom_id: str):
        url = f"{self.base_url}/removeTopMsg"
        json_para = json_remove_top_msg(msg_id, chatroom_id)
        response = requests.post(url, data=json_para)
        return response.json()

    def remove_top_msg(self, msg_id: str, chatroom_id: str):
        """
        Remove a top message in chatroom. Chatroom admin is needed
        :param msg_id: The message identifier
        :param chatroom_id: Chatroom identifier
        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_remove_top_msg(msg_id, chatroom_id)
        if json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_invite_member_to_chatroom(self, chatroom_id: str, wxids: list):
        url = f"{self.base_url}/InviteMemberToChatRoom"
        json_para = json_invite_member_to_chatroom(chatroom_id, wxids)
        response = requests.post(url, data=json_para)
        return response.json()

    def invite_member_to_chatroom(self, chatroom_id: str, wxids: list):
        """
        Invite to join the chatroom, (Chatrooms of more than 40 people need to use this invitation to join the group)
        :param chatroom_id: Chatroom identifier
        :param wxids: The list of wxid you want to invite
        :return:
        """
        json_response = self.raw_invite_member_to_chatroom(chatroom_id, wxids)
        if json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_hook_log(self):
        url = f"{self.base_url}/hookLog"
        json_para = json_hook_log()
        response = requests.post(url, data=json_para)
        return response.json()

    def hook_log(self) -> bool:
        """
        hook WeChat logs. The output is in the logs directory of the WeChat installation directory
        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_hook_log()
        if json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_unhook_log(self):
        url = f"{self.base_url}/unhookLog"
        json_para = json_unhook_log()
        response = requests.post(url, data=json_para)
        return response.json()

    def unhook_log(self) -> bool:
        """
        unhook WeChat logs
        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_unhook_log()
        if json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_create_chatroom(self, wxids: list):
        url = f"{self.base_url}/createChatRoom"
        json_para = json_create_chatroom(wxids)
        response = requests.post(url, data=json_para)
        return response.json()

    def create_chatroom(self, wxids: list) -> bool:
        """
        Create a chatroom. USE WITH CAUTIOUS, HIGH CHANCE OF GETTING BANNED.
        :param wxids: The list of wxid you want to create chatroom
        :return: A dictionary, including: chatRoomId(string) chatRoomName(string) notice(string) admin(int) \
        xml information(list).
        """
        json_response = self.raw_create_chatroom(wxids)
        if json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_quit_chatroom(self, chatroom_id: str):
        url = f"{self.base_url}/quitChatRoom"
        json_para = json_quit_chatroom(chatroom_id)
        response = requests.post(url, data=json_para)
        return response.json()

    def quit_chatroom(self, chatroom_id: str) -> bool:
        """
        Quit the chatroom
        :param chatroom_id: Chatroom identifier
        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_quit_chatroom(chatroom_id)
        if json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_forward_msg(self, wxid: str, msg_id: str):
        url = f"{self.base_url}/forwardMsg"
        json_para = json_forward_msg(wxid, msg_id)
        response = requests.post(url, data=json_para)
        return response.json()

    def forward_msg(self, wxid: str, msg_id: str) -> bool:
        """
        Forward the message to the wxid
        :param wxid: WeChat account identifier
        :param msg_id: The message identifier
        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_forward_msg(wxid, msg_id)
        if json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_get_sns_first_page(self):
        url = f"{self.base_url}/getSNSFirstPage"
        json_para = json_get_sns_first_page()
        response = requests.post(url, data=json_para)
        return response.json()

    def get_sns_first_page(self):
        """
        Get the first page of SNS. The SNS information will be sent to the message tcp server. The format is:
        {"data":[{"content": "","createTime': 1691125287,"senderId': "", "snsId': 123,"xml':""}]}
        :return: A dictionary, including: SNS information(list)
        """
        json_response = self.raw_get_sns_first_page()
        if json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_get_sns_next_page(self, sns_id: int):
        url = f"{self.base_url}/getSNSNextPage"
        json_para = json_get_sns_next_page(sns_id)
        response = requests.post(url, data=json_para)
        return response.json()

    def get_sns_next_page(self, sns_id: int):
        """
        Get the next page of SNS. The SNS information will be sent to the message tcp server. The format is:
        {"data":[{"content": "","createTime': 1691125287,"senderId': "", "snsId': 123,"xml':""}]}
        :param sns_id: The sns identifier
        :return: A dictionary, including: SNS information(list)
        """
        json_response = self.raw_get_sns_next_page(sns_id)
        if json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_add_fav_from_msg(self, msg_id: str):
        url = f"{self.base_url}/addFavFromMsg"
        json_para = json_add_fav_from_msg(msg_id)
        response = requests.post(url, data=json_para)
        return response.json()

    def add_fav_from_msg(self, msg_id: str) -> bool:
        """
        Add the message to favorite
        :param msg_id: The message identifier
        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_add_fav_from_msg(msg_id)
        if json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_add_fav_from_image(self, wxid: str, image_path: str):
        url = f"{self.base_url}/addFavFromImage"
        json_para = json_add_fav_from_image(wxid, image_path)
        response = requests.post(url, data=json_para)
        return response.json()

    def raw_send_at_msg(self, chatroom_id: str, msg: str, wxids: list):
        url = f"{self.base_url}/sendAtText"
        json_para = json_send_at_msg(chatroom_id, msg, wxids)
        response = requests.post(url, data=json_para)
        return response.json()

    def send_at_msg(self, chatroom_id: str, msg: str, wxids: list) -> bool:
        """
        Send an @ message to the chatroom. To @all, add "notify@all" in the wxids list.
        :param chatroom_id: Chatroom identifier
        :param msg: The message you want to send
        :param wxids: The list of wxid you want to at
        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_send_at_msg(chatroom_id, msg, wxids)
        if json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_get_contact_profile(self, wxid: str):
        url = f"{self.base_url}/getContactProfile"
        json_para = json_get_contact_profile(wxid)
        response = requests.post(url, data=json_para)
        return response.json()

    def get_contact_profile(self, wxid: str) -> dict:
        """
        Get the contact profile
        :param wxid: WeChat account identifier
        :return: A dictionary, including: wxid(string) account(string) headImage(string) nickname(string) v3(string)
        """
        json_response = self.raw_get_contact_profile(wxid)
        data = json_response.get('data')
        return data

    def raw_send_public_msg(self, wxid: str, app_name: str, user_name: str, title: str, msg_url: str, thumb_url: str,
                            digest: str):
        url = f"{self.base_url}/forwardPublicMsg"
        json_para = json_send_public_msg(wxid, app_name, user_name, title, msg_url, thumb_url, digest)
        response = requests.post(url, data=json_para)
        return response.json()

    def send_public_msg(self, wxid: str, app_name: str, user_name: str, title: str, url: str, thumb_url: str,
                        digest: str) -> bool:
        """
        Send a public message
        :param wxid: WeChat account identifier
        :param app_name: The app name
        :param user_name: The username
        :param title: The title of the message
        :param url: The url of the message
        :param thumb_url: The thumb url of the message
        :param digest: The digest of the message
        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_send_public_msg(wxid, app_name, user_name, title, url, thumb_url, digest)
        if json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_forward_public_msg_by_msg_id(self, wxid: str, msg_id: str):
        url = f"{self.base_url}/forwardPublicMsgByMsgId"
        json_para = json_forward_public_msg_by_msg_id(wxid, msg_id)
        response = requests.post(url, data=json_para)
        return response.json()

    def forward_public_msg_by_msg_id(self, wxid: str, msg_id: str) -> bool:
        """
        Forward a public message by message id to a wxid
        :param wxid: WeChat account identifier
        :param msg_id: The message identifier of public message
        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_forward_public_msg_by_msg_id(wxid, msg_id)
        if json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_download_attach(self, msg_id: str):
        url = f"{self.base_url}/downloadAttach"
        json_para = json_download_attach(msg_id)
        response = requests.post(url, data=json_para)
        return response.json()

    def download_attach(self, msg_id: str) -> bool:
        """
        Download the attachment of the message. Saved in the wxid_xxx/wxhelper directory in the WeChat file directory.

        :param msg_id: The message identifier
        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_download_attach(msg_id)
        if json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_decode_image(self, file_path: str, store_dir: str):
        url = f"{self.base_url}/decodeImage"
        json_para = json_decode_image(file_path, store_dir)
        response = requests.post(url, data=json_para)
        return response.json()

    def decode_image(self, file_path: str, store_dir: str) -> bool:
        """
        Decode the image
        :param file_path: The input path of the image
        :param store_dir: The output store directory
        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_decode_image(file_path, store_dir)
        if json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_get_voice_by_msg_id(self, msg_id: str, store_dir: str):
        url = f"{self.base_url}/getVoiceByMsgId"
        json_para = json_get_voice_by_msg_id(msg_id, store_dir)
        response = requests.post(url, data=json_para)
        return response.json()

    def get_voice_by_msg_id(self, msg_id: str, store_dir: str) -> bool:
        """
        Get the voice by message id
        :param msg_id: The message identifier
        :param store_dir: The store directory
        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_get_voice_by_msg_id(msg_id, store_dir)
        if json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_send_custom_emotion(self, wxid: str, file_path: str):
        url = f"{self.base_url}/sendCustomEmotion"
        json_para = json_send_custom_emotion(wxid, file_path)
        response = requests.post(url, data=json_para)
        return response.json()

    def send_custom_emotion(self, wxid: str, file_path: str) -> bool:
        """
        Send a custom emotion
        :param wxid: WeChat account identifier
        :param file_path: The path of the emotion. You can query MD5 fields in the CustomEmotion table. \
        For the path rules, see the following example:
        "C:\\wechatDir\\WeChat Files\\wxid_123\\FileStorage\\CustomEmotion\\8F\\8F6423BC2E69188DCAC797E279C81DE9"

        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_send_custom_emotion(wxid, file_path)
        if json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_send_applet_msg(self, wxid: str, waid_concat: str, applet_wxid: str, json_param: str, head_img_url: str,
                            main_img: str, index_page: str):
        url = f"{self.base_url}/sendApplet"
        json_para = json_send_applet(wxid, waid_concat, applet_wxid, json_param, head_img_url, main_img, index_page)
        response = requests.post(url, data=json_para)
        return response.json()

    def send_applet_msg(self, wxid: str, waid_concat: str, applet_wxid: str, json_param: str, head_img_url: str,
                        main_img: str,
                        index_page: str) -> bool:
        """
        Send an applet message. THIS FUNCTION IS NOT STABLE.
        :param wxid: WeChat account identifier
        :param waid_concat: The information of wxid adding to invoke information. This param can be counterfeited.
        :param applet_wxid: The applet wxid
        :param json_param: Related parameters
        :param head_img_url: The head image url
        :param main_img: The main image of the applet, needs to be in the temporary directory of the applet. \
         Ex: C:\\wxid_123123\\Applet\\wxaf35009675aa0b2a\\temp\\

        :param index_page: The jump page of applet.
        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_send_applet_msg(wxid, waid_concat, applet_wxid, json_param, head_img_url, main_img,
                                                 index_page)
        if json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_send_pat_msg(self, wxid: str, receiver: str):
        url = f"{self.base_url}/sendPatMsg"
        json_para = json_send_pat_msg(wxid, receiver)
        response = requests.post(url, data=json_para)
        return response.json()

    def send_pat_msg(self, wxid: str, patter: str) -> bool:
        """
        Send a pat message
        :param wxid: WeChat account identifier
        :param patter: The receiver wxid. Can be their own wxid, private chat friends wxid, chatroom id
        :return: Boolean. True if success, False if failed.
        """
        json_response = self.raw_send_pat_msg(wxid, patter)
        if json_response.get('code') == -1:
            return False
        else:
            return True

    def raw_ocr(self, image_path: str):
        url = f"{self.base_url}/ocr"
        json_para = json_ocr(image_path)
        response = requests.post(url, data=json_para)
        return response.json()

    def ocr(self, image_path: str) -> dict:
        """
        ocr the image
        :param image_path: The path of the image
        :return: A dictionary, including: code(int) data(string). The data is the result of the ocr.
        """
        json_response = self.raw_ocr(image_path)
        if json_response.get('code') != 0:
            json_response = self.raw_ocr(image_path)
            return json_response
        return json_response
