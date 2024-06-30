import platform
import subprocess

import requests

from utils.web_api_data import WebApiData
from .pywxdll_json import *


class Pywxdll:
    def __init__(self, ip='127.0.0.1', port=19088):  # 微信hook服务器的ip地址和端口 The ip and port for wechat hook server
        """
        :param ip:
        :param port:
        """
        self.ip = ip
        self.port = port
        self.base_url = f"http://{ip}:{port}/api"

        self.docker_injector_path = "pywxdll/Injector_Docker.exe"
        self.windows_wechat_start_path = "pywxdll/StartWxAndInject_Windows.exe"
        self.dll_path = "pywxdll/wxhelper-3.9.5.81-v11.dll"
        self.injection_process_name = "WeChat.exe"
        self.wechatVersionFixPath = "pywxdll/fixWechatVersion.py"

        self._web_api_data = WebApiData()

    def _injectDLL(self):
        """
        This function is to inject the wxhelper dll into WeChat process in Docker environment
        :return: True if success, False if failed.
        """
        result = subprocess.run(
            f"wine {self.docker_injector_path} --process-name {self.injection_process_name} --inject {self.dll_path}",
            shell=True, stdout=subprocess.PIPE)

        # The injector has a bug that it returns Call to LoadLibraryW in remote process failed. even if the injection is successful
        if "Call to LoadLibraryW in remote process failed." in result or "Successfully injected module!" in result:
            return True
        else:
            return False

    def _startWeChatAndInject(self):
        """
        This function is to start WeChat and inject the wxhelper dll on Windows environment
        :return:
        """
        result = subprocess.run(f"{self.windows_wechat_start_path} {self.dll_path} {self.port}", shell=True,
                                stdout=subprocess.PIPE)

        if result:
            return True
        else:
            return False

    def _fixWechatVersion(self) -> bool:
        """
        This function is to fix the WeChat version
        :return: True if success, Flase if failed.
        """
        if platform.system() == 'Windows':
            pythonCommand = 'python'
        else:
            pythonCommand = 'wine python'

        result = subprocess.run(f"{pythonCommand} {self.wechatVersionFixPath}", shell=True, stdout=subprocess.PIPE)

        if 'Fix Success' in result:
            return True
        else:
            return False

    def rawIsLoggedIn(self) -> dict:
        url = f"{self.base_url}/checkLogin"
        jsonPara = jsonIsLoggedIn()
        response = requests.post(url, data=jsonPara)
        return response.json()

    def isLoggedIn(self) -> bool:
        """
        Check if the wechat is logged in or not.
        :return: A boolean, True if logged in, False if not logged in.
        """
        jsonResponse = self.rawIsLoggedIn()
        if jsonResponse.get('code') == 1:
            return True
        else:
            return False

    def rawGetLoggedInAccountInfo(self):
        url = f"{self.base_url}/userInfo"
        jsonPara = jsonGetLoggedInAccountInfo()
        response = requests.post(url, data=jsonPara)
        return response.json()

    def getLoggedInAccountInfo(self) -> dict:
        """
        Get information of the account logged into.
        :return: A dictionary, including: wxid(string) account(string) headImage(string) city(string) country(string) currentDataPath(string) dataSavePath(string) mobile(string) name(string) province(string) signature(string)
        """
        jsonResponse = self.rawGetLoggedInAccountInfo()
        data = jsonResponse.get('data')
        return data

    def rawSendTextMsg(self, wxid: str, msg: str):
        url = f"{self.base_url}/sendTextMsg"
        jsonPara = jsonSendTextMsg(wxid, msg)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def sendTextMsg(self, wxid: str, msg: str) -> bool:
        """
        Send a text message to the wxid.
        :param wxid: Wechat account identifier
        :param msg: The message needed to send
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawSendTextMsg(wxid, msg)
        if jsonResponse.get('code') == 0 or jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawSendImageMsg(self, wxid: str, imagePath: str):
        url = f"{self.base_url}/sendImagesMsg"
        jsonPara = jsonSendImageMsg(wxid, imagePath)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def sendImageMsg(self, wxid: str, imagePath: str) -> bool:
        """
        Send a picture message to the wxid.
        :param wxid: Wechat account identifier
        :param imagePath: The path of the image
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawSendImageMsg(wxid, imagePath)
        if jsonResponse.get('code') == 0 or jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawSendFileMsg(self, wxid: str, filePath: str):
        url = f"{self.base_url}/sendFileMsg"
        jsonPara = jsonSendFileMsg(wxid, filePath)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def sendFileMsg(self, wxid: str, filePath: str) -> bool:
        """
        Send a file message to the wxid.
        :param wxid: Wechat account identifier
        :param filePath: The path of the file
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawSendFileMsg(wxid, filePath)
        if jsonResponse.get('code') == 0 or jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawStartHookMsg(self, port: int, ip: str, hookUrl: str = '', timeout: int = 3000, enableHttp: bool = False):
        url = f"{self.base_url}/hookSyncMsg"
        jsonPara = jsonStartHookMsg(port, ip, hookUrl, timeout, enableHttp)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def startHookMsg(self, port: int, ip: str = '127.0.0.1', hookUrl: str = '', timeout: int = 3000,
                     enableHttp: bool = False) -> bool:
        """
        Start hooking the message and send to the tcp server
        :param port: The port of tcp server
        :param ip: The ip of tcp server
        :param hookUrl: Optional, the url of the tcp server. When enableHttp is True, this is required.
        :param timeout: Optional, the timeout of sending tcp request, default is 3000ms
        :param enableHttp: Optional, enable http or not, default is False
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawStartHookMsg(port, ip, hookUrl, timeout, enableHttp)
        if jsonResponse.get('code') == 0 or jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawStopHookMsg(self):
        url = f"{self.base_url}/unhookSyncMsg"
        jsonPara = jsonStopHookMsg()
        response = requests.post(url, data=jsonPara)
        return response.json()

    def stopHookMsg(self) -> bool:
        """
        Stop the hook server
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawStopHookMsg()
        if jsonResponse.get('code') == 0:
            return True
        else:
            return False

    def rawGetContectList(self):
        url = f"{self.base_url}/getContactList"
        jsonPara = jsonGetContactList()
        response = requests.post(url, data=jsonPara)
        return response.json()

    def getContactList(self) -> list:
        """
        Get the contact list
        :return: A list of contact information
        """
        jsonResponse = self.rawGetContectList()
        data = jsonResponse.get('data')
        return data

    def rawGetDBInfo(self):
        url = f"{self.base_url}/getDBInfo"
        jsonPara = jsonGetDBInfo()
        response = requests.post(url, data=jsonPara)
        return response.json()

    def getDBInfo(self) -> dict:
        """
        Gets database information and handles
        :return: Information of database. Including database name(string), handle(int), tables(list), name(string), rootpage(string), sql(string), table name(string).
        """
        jsonResponse = self.rawGetDBInfo()
        data = jsonResponse.get('data')
        return data

    def rawExecSql(self, dbHandle: int, sql: str):
        url = f"{self.base_url}/execSql"
        jsonPara = jsonExecSql(dbHandle, sql)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def execSql(self, dbHandle: int, sql: str) -> list:
        """
        Execute the sql command in WeChat database
        :param dbHandle: The handle of the database
        :param sql: The sql command
        :return: The result of the sql command
        """
        jsonResponse = self.rawExecSql(dbHandle, sql)
        data = jsonResponse.get('data')
        return data

    def rawGetChatRoomDetailInfo(self, chatRoomId: str):
        url = f"{self.base_url}/getChatRoomDetailInfo"
        jsonPara = jsonGetChatRoomDetailInfo(chatRoomId)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def getChatRoomDetailInfo(self, chatRoomId: str) -> dict:
        """
        Get chatroom details
        :param chatRoomId:
        :return: A dictionary, including: chatRoomId(string) chatRoomName(string) notice(string) admin(int) xml information(list).
        """
        jsonResponse = self.rawGetChatRoomDetailInfo(chatRoomId)
        data = jsonResponse.get('data')
        return data

    def rawAddMemberToChatRoom(self, chatRoomId: str, wxids: list):
        url = f"{self.base_url}/addMemberToChatRoom"
        jsonPara = jsonAddMemberToChatRoom(chatRoomId, wxids)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def addMemberToChatRoom(self, chatRoomId: str, wxids: list) -> bool:
        """
        Add members to chatroom
        :param chatRoomId: Chatroom identifier
        :param wxids: The list of wxid you want to add
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawAddMemberToChatRoom(chatRoomId, wxids)
        if jsonResponse.get('code') == 1:
            return True
        else:
            return False

    def rawModifyNickname(self, chatRoomId: str, wxid: str, nickName: str):
        url = f"{self.base_url}/modifyNickname"
        jsonPara = jsonModifyNickname(chatRoomId, wxid, nickName)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def modifyNickname(self, chatRoomId: str, wxid: str, nickName: str) -> bool:
        """
        Modify the nickname in chatroom
        :param chatRoomId: Chatroom identifier
        :param wxid: The wxid you want to modify
        :param nickName: The nickname you want to modify
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawModifyNickname(chatRoomId, wxid, nickName)
        if jsonResponse.get('code') == 1:
            return True
        else:
            return False

    def rawDelMemberFromChatRoom(self, chatRoomId: str, wxids: list):
        url = f"{self.base_url}/delMemberFromChatRoom"
        jsonPara = jsonDelMemberFromChatRoom(chatRoomId, wxids)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def delMemberFromChatRoom(self, chatRoomId: str, wxids: list) -> bool:
        """
        Delete members from chatroom
        :param chatRoomId: Chatroom identifier
        :param wxids: The list of wxid you want to delete
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawDelMemberFromChatRoom(chatRoomId, wxids)
        if jsonResponse.get('code') == 1:
            return True
        else:
            return False

    def rawGetMemberFromChatRoom(self, chatRoomId: str):
        url = f"{self.base_url}/getMemberFromChatRoom"
        jsonPara = jsonGetMemberFromChatRoom(chatRoomId)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def getMemberFromChatRoom(self, chatRoomId: str) -> dict:
        """
        Get members from chatroom
        :param chatRoomId: Chatroom identifier
        :return: A dictionary, including: admin(string) adminNickname(string) chatRoomId(string) memberNickname(string) members(string).
        """
        jsonResponse = self.rawGetMemberFromChatRoom(chatRoomId)
        data = jsonResponse.get('data')
        data['memberNickname'] = data.get('memberNickname').split('^G')
        data['members'] = data.get('members').split('^G')
        return data

    def rawTopMsg(self, msgId: str):
        url = f"{self.base_url}/topMsg"
        jsonPara = jsonTopMsg(msgId)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def topMsg(self, msgId: str):
        """
        Top a message in chatroom. Chatroom admin is needed
        :param msgId: The message identifier
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawTopMsg(msgId)
        if jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawRemoveTopMsg(self, msgId: str, chatRoomId: str):
        url = f"{self.base_url}/removeTopMsg"
        jsonPara = jsonRemoveTopMsg(msgId, chatRoomId)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def removeTopMsg(self, msgId: str, chatRoomId: str):
        """
        Remove a top message in chatroom. Chatroom admin is needed
        :param msgId: The message identifier
        :param chatRoomId: Chatroom identifier
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawRemoveTopMsg(msgId, chatRoomId)
        if jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawInviteMemberToChatRoom(self, chatRoomId: str, wxids: list):
        url = f"{self.base_url}/InviteMemberToChatRoom"
        jsonPara = jsonInviteMemberToChatRoom(chatRoomId, wxids)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def inviteMemberToChatRoom(self, chatRoomId: str, wxids: list):
        """
        Invite to join the chatroom, (Chatrooms of more than 40 people need to use this invitation to join the group)
        :param chatRoomId: Chatroom identifier
        :param wxids: The list of wxid you want to invite
        :return:
        """
        jsonResponse = self.rawInviteMemberToChatRoom(chatRoomId, wxids)
        if jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawHookLog(self):
        url = f"{self.base_url}/hookLog"
        jsonPara = jsonHookLog()
        response = requests.post(url, data=jsonPara)
        return response.json()

    def hookLog(self) -> bool:
        """
        hook wechat logs. The output is in the logs directory of the wechat installation directory
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawHookLog()
        if jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawUnhookLog(self):
        url = f"{self.base_url}/unhookLog"
        jsonPara = jsonUnhookLog()
        response = requests.post(url, data=jsonPara)
        return response.json()

    def unhookLog(self) -> bool:
        """
        unhook wechat logs
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawUnhookLog()
        if jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawCreateChatroom(self, wxids: list):
        url = f"{self.base_url}/createChatRoom"
        jsonPara = jsonCreateChatroom(wxids)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def createChatroom(self, wxids: list) -> bool:
        """
        Create a chatroom. USE WITH CAUTIOUS, HIGH CHANCE OF GETTING BANNED.
        :param wxids: The list of wxid you want to create chatroom
        :return: A dictionary, including: chatRoomId(string) chatRoomName(string) notice(string) admin(int) xml information(list).
        """
        jsonResponse = self.rawCreateChatroom(wxids)
        if jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawQuitChatroom(self, chatRoomId: str):
        url = f"{self.base_url}/quitChatRoom"
        jsonPara = jsonQuitChatroom(chatRoomId)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def quitChatroom(self, chatRoomId: str) -> bool:
        """
        Quit the chatroom
        :param chatRoomId: Chatroom identifier
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawQuitChatroom(chatRoomId)
        if jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawForwardMsg(self, wxid: str, msgId: str):
        url = f"{self.base_url}/forwardMsg"
        jsonPara = jsonForwardMsg(wxid, msgId)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def forwardMsg(self, wxid: str, msgId: str) -> bool:
        """
        Forward the message to the wxid
        :param wxid: Wechat account identifier
        :param msgId: The message identifier
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawForwardMsg(wxid, msgId)
        if jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawGetSNSFirstPage(self):
        url = f"{self.base_url}/getSNSFirstPage"
        jsonPara = jsonGetSNSFirstPage()
        response = requests.post(url, data=jsonPara)
        return response.json()

    def getSNSFirstPage(self):
        """
        Get the first page of SNS. The SNS information will be send to the message tcp server. The format is:
        {"data":[{"content": "","createTime': 1691125287,"senderId': "", "snsId': 123,"xml':""}]}
        :return: A dictionary, including: SNS information(list)
        """
        jsonResponse = self.rawGetSNSFirstPage()
        if jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawGetSNSNextPage(self, snsId: int):
        url = f"{self.base_url}/getSNSNextPage"
        jsonPara = jsonGetSNSNextPage(snsId)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def getSNSNextPage(self, snsId: int):
        """
        Get the next page of SNS. The SNS information will be send to the message tcp server. The format is:
        {"data":[{"content": "","createTime': 1691125287,"senderId': "", "snsId': 123,"xml':""}]}
        :param snsId: The sns identifier
        :return: A dictionary, including: SNS information(list)
        """
        jsonResponse = self.rawGetSNSNextPage(snsId)
        if jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawAddFavFromMsg(self, msgId: str):
        url = f"{self.base_url}/addFavFromMsg"
        jsonPara = jsonAddFavFromMsg(msgId)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def addFavFromMsg(self, msgId: str) -> bool:
        """
        Add the message to favorite
        :param msgId: The message identifier
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawAddFavFromMsg(msgId)
        if jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawAddFavFromImage(self, wxid: str, imagePath: str):
        url = f"{self.base_url}/addFavFromImage"
        jsonPara = jsonAddFavFromImage(wxid, imagePath)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def rawSendAtMsg(self, chatRoomId: str, msg: str, wxids: list):
        url = f"{self.base_url}/sendAtText"
        jsonPara = jsonSendAtMsg(chatRoomId, msg, wxids)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def sendAtMsg(self, chatRoomId: str, msg: str, wxids: list) -> bool:
        """
        Send an @ message to the chatroom. To @all, add "notify@all" in the wxids list.
        :param chatRoomId: Chatroom identifier
        :param msg: The message you want to send
        :param wxids: The list of wxid you want to at
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawSendAtMsg(chatRoomId, msg, wxids)
        if jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawGetContactProfile(self, wxid: str):
        url = f"{self.base_url}/getContactProfile"
        jsonPara = jsonGetContactProfile(wxid)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def getContactProfile(self, wxid: str) -> dict:
        """
        Get the contact profile
        :param wxid: Wechat account identifier
        :return: A dictionary, including: wxid(string) account(string) headImage(string) nickname(string) v3(string)
        """
        jsonResponse = self.rawGetContactProfile(wxid)
        data = jsonResponse.get('data')
        return data

    def rawSendPublicMsg(self, wxid: str, appName: str, userName: str, title: str, url: str, thumbUrl: str,
                         digest: str):
        url = f"{self.base_url}/forwardPublicMsg"
        jsonPara = jsonSendPublicMsg(wxid, appName, userName, title, url, thumbUrl, digest)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def SendPublicMsg(self, wxid: str, appName: str, userName: str, title: str, url: str, thumbUrl: str,
                      digest: str) -> bool:
        """
        Send a public message
        :param wxid: Wechat account identifier
        :param appName: The app name
        :param userName: The user name
        :param title: The title of the message
        :param url: The url of the message
        :param thumbUrl: The thumb url of the message
        :param digest: The digest of the message
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawSendPublicMsg(wxid, appName, userName, title, url, thumbUrl, digest)
        if jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawForwardPublicMsgByMsgId(self, wxid: str, msgId: str):
        url = f"{self.base_url}/forwardPublicMsgByMsgId"
        jsonPara = jsonForwardPublicMsgByMsgId(wxid, msgId)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def forwardPublicMsgByMsgId(self, wxid: str, msgId: str) -> bool:
        """
        Forward a public message by message id to a wxid
        :param wxid: Wechat account identifier
        :param msgId: The message identifier of public message
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawForwardPublicMsgByMsgId(wxid, msgId)
        if jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawDownloadAttach(self, msgId: str):
        url = f"{self.base_url}/downloadAttach"
        jsonPara = jsonDownloadAttach(msgId)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def downloadAttach(self, msgId: str) -> bool:
        """
        Download the attachment of the message. Saved in the wxid_xxx/wxhelper directory in the wechat file directory.

        :param msgId: The message identifier
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawDownloadAttach(msgId)
        if jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawDecodeImage(self, filePath: str, storeDir: str):
        url = f"{self.base_url}/decodeImage"
        jsonPara = jsonDecodeImage(filePath, storeDir)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def decodeImage(self, filePath: str, storeDir: str) -> bool:
        """
        Decode the image
        :param filePath: The input path of the image
        :param storeDir: The output store directory
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawDecodeImage(filePath, storeDir)
        if jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawGetVoiceByMsgId(self, msgId: str, storeDir: str):
        url = f"{self.base_url}/getVoiceByMsgId"
        jsonPara = jsonGetVoiceByMsgId(msgId, storeDir)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def getVoiceByMsgId(self, msgId: str, storeDir: str) -> bool:
        """
        Get the voice by message id
        :param msgId: The message identifier
        :param storeDir: The store directory
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawGetVoiceByMsgId(msgId, storeDir)
        if jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawSendCustomEmotion(self, wxid: str, filePath: str):
        url = f"{self.base_url}/sendCustomEmotion"
        jsonPara = jsonSendCustomEmotion(wxid, filePath)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def sendCustomEmotion(self, wxid: str, filePath: str) -> bool:
        """
        Send a custom emotion
        :param wxid: Wechat account identifier
        :param filePath: The path of the emotion. You can query MD5 fields in the CustomEmotion table. For the path rules, see the following example: C:\\wechatDir\\WeChat Files\\wxid_123\\FileStorage\\CustomEmotion\\8F\\8F6423BC2E69188DCAC797E279C81DE9
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawSendCustomEmotion(wxid, filePath)
        if jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawSendAppletMsg(self, wxid: str, waidConcat: str, appletWxid: str, jsonParam: str, headImgUrl: str,
                         mainImg: str, indexPage: str):
        url = f"{self.base_url}/sendApplet"
        jsonPara = jsonSendApplet(wxid, waidConcat, appletWxid, jsonParam, headImgUrl, mainImg, indexPage)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def sendAppletMsg(self, wxid: str, waidConcat: str, appletWxid: str, jsonParam: str, headImgUrl: str, mainImg: str,
                      indexPage: str) -> bool:
        """
        Send an applet message. THIS FUNCTION IS NOT STABLE.
        :param wxid: Wechat account identifier
        :param waidConcat: The information of wxid adding to invoke information. This param can be counterfeited.
        :param appletWxid: The applet wxid
        :param jsonParam: Related parameters
        :param headImgUrl: The head image url
        :param mainImg: The main image of the applet, needs to be in the temporary directory of the applet. Ex: C:\\wxid_123123\\Applet\\wxaf35009675aa0b2a\\temp\\
        :param indexPage: The jump page of applet.
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawSendAppletMsg(wxid, waidConcat, appletWxid, jsonParam, headImgUrl, mainImg, indexPage)
        if jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawSendPatMsg(self, wxid: str, receiver: str):
        url = f"{self.base_url}/sendPatMsg"
        jsonPara = jsonSendPatMsg(wxid, receiver)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def sendPatMsg(self, wxid: str, patter: str) -> bool:
        """
        Send a pat message
        :param wxid: Wechat account identifier
        :param patter: The receiver wxid. Can be their own wxid, private chat friends wxid, chatroom id
        :return: Boolean. True if success, False if failed.
        """
        jsonResponse = self.rawSendPatMsg(wxid, patter)
        if jsonResponse.get('code') == -1:
            return False
        else:
            return True

    def rawOCR(self, imagePath: str):
        url = f"{self.base_url}/ocr"
        jsonPara = jsonOCR(imagePath)
        response = requests.post(url, data=jsonPara)
        return response.json()

    def OCR(self, imagePath: str) -> dict:
        """
        OCR the image
        :param imagePath: The path of the image
        :return: A dictionary, including: code(int) data(string). The data is the result of the OCR.
        """
        jsonResponse = self.rawOCR(imagePath)
        if (jsonResponse.get('code') != 0):
            jsonResponse = self.rawOCR(imagePath)
            return jsonResponse
        return jsonResponse
