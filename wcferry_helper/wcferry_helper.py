#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import asyncio
import subprocess
import time
from os import path
from platform import system

import xmltodict
from wcferry import wxmsg, client


def inject(port: int = 5555, debug: bool = False, local: bool = True):
    """
    Inject WeChat Ferry into the WeChat.
    :param port: The port.
    :param debug: Whether to enable debug mode.
    :param local: Whether to run the injector locally.
    """
    if not local:
        return

    sys = system()
    if sys == "Windows":
        abs_inject_dir = path.abspath("wcferry_helper")
        proccess = subprocess.Popen(f"wcferry_helper/injector.exe {port} {debug}", shell=True, cwd=abs_inject_dir)
    elif sys == "Linux":
        proccess = subprocess.Popen(f"wine wcferry_helper/injector.exe {port} {debug}", shell=True)
    else:
        raise NotImplementedError(f"Unsupported system: {sys}")

    time.sleep(10)

    return proccess


def wxmsg_formatter(message: wxmsg.WxMsg) -> str:
    """
    Format the received message.
    :param message: The received message.
    :return: The formatted message.
    """
    formatted_xml = str(message.xml).replace("\n", "").replace(" ", "")
    formatted = f"sender:{message.sender} roomid:{message.roomid} type:{message.type} id:{message.id} content:{message.content} thumb:{message.thumb} extra:{message.extra} from_group:{message.from_group()} from_self:{message.from_self()} is_text:{message.is_text()} xml:{formatted_xml}"
    return formatted


def wxmsg_to_dict(message: wxmsg.WxMsg) -> dict:
    """
    Convert the received message to a dictionary.
    :param message: The received message.
    :return: The dictionary.
    """
    dictionary = {
        "sender": message.sender,
        "roomid": message.roomid,
        "type": message.type,
        "id": message.id,
        "content": message.content,
        "thumb": message.thumb,
        "extra": message.extra,
        "from_group": message.from_group(),
        "from_self": message.from_self(),
        "is_text": message.is_text(),
        "is_at": message.is_at,
        "xml": message.xml
    }
    return dictionary


class XYBotWxMsg:
    def __init__(self, msg: wxmsg.WxMsg):
        self._is_self = msg.from_self()
        self._is_group = msg.from_group()
        self.type = msg.type
        self.id = msg.id
        self.ts = msg.ts
        self.sign = msg.sign
        self.xml = msg.xml
        self.sender = msg.sender
        self.roomid = msg.roomid
        self.content = msg.content
        self.thumb = msg.thumb
        self.extra = msg.extra
        self.ats = []
        self.image = ""
        self.voice = ""
        self.join_group = ""

        # 处理xml
        self.xml = xmltodict.parse(self.xml.replace('\\n|\\t| ', ''))  # 将xml转换为字典

        # @ 信息
        if self.from_group():
            at_user_list = self.xml.get('msgsource', {}).get('atuserlist', "")
            if at_user_list:
                self.ats = at_user_list.split(',')

    def __str__(self):
        _dict = {
            "sender": self.sender,
            "roomid": self.roomid,
            "type": self.type,
            "id": self.id,
            "content": self.content,
            "thumb": self.thumb,
            "extra": self.extra,
            "from_group": self.from_group(),
            "from_self": self.from_self(),
            "is_text": self.is_text(),
            "is_at": self.is_at,
            "xml": self.xml,
            "ats": self.ats,
            "join_group": self.join_group,
        }
        return str(_dict)

    def from_self(self) -> bool:
        """是否自己发的消息"""
        return self._is_self == 1

    def from_group(self) -> bool:
        """是否群聊消息"""
        return self._is_group

    def is_at(self, wxid) -> bool:
        """是否被 @：群消息，在 @ 名单里，并且不是 @ 所有人"""
        if not self.from_group():
            return False  # 只有群消息才能 @

        if wxid not in self.ats:
            return False  # 不在 @ 清单里

        if "@所有人" not in self.content and "@all" not in self.content and "@All" not in self.content:
            return False  # 排除 @ 所有人

        return True

    def is_text(self) -> bool:
        """是否文本消息"""
        return self.type == 1


async def async_download_image(bot: client.Wcf, id: int, extra: str, dir: str, timeout: int = 30) -> str:
    """
    Download the image asynchronously.
    :param bot: The bot.
    :param id: The id.
    :param extra: The extra.
    :param dir: The directory.
    :param timeout: The timeout.
    :return: The path of the downloaded image, or an empty string if the download failed.
    """
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, bot.download_image, id, extra, dir, timeout)
    return result


async def async_get_audio_msg(bot: client.Wcf, id: int, dir: str, timeout: int = 30) -> str:
    """
    Get the audio message asynchronously.
    :param bot: The bot.
    :param id: The id.
    :param dir: The directory.
    :param timeout: The timeout.
    :return: The path of the audio message, or an empty string if the download failed.
    """
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, bot.get_audio_msg, id, dir, timeout)
    return result
