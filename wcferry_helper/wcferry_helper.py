#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import subprocess
from platform import system

from wcferry import wxmsg


def inject(port: int = 5555, debug: bool = False, local: bool = True):
    """
    Inject WeChat Ferry into the WeChat.
    :param port: The port.
    :param debug: Whether to enable debug mode.
    """
    if local:
        return

    sys = system()
    if sys == "Windows":
        subprocess.run(f"injector.exe {port} {debug}", shell=True, cwd="wcferry_helper")
    elif sys == "Linux":
        subprocess.run(f"wine injector.exe {port} {debug}", shell=True, cwd="wcferry_helper")
    else:
        raise NotImplementedError(f"Unsupported system: {sys}")

def wxmsg_formatter(message: wxmsg.WxMsg) -> str:
    """
    Format the received message.
    :param recv: The received message.
    :return: The formatted message.
    """
    formatted_xml = str(message.xml).replace("\n", "").replace(" ","")
    formatted =  f"sender:{message.sender} roomid:{message.roomid} type:{message.type} id:{message.id} content:{message.content} thumb:{message.thumb} extra:{message.extra} from_group:{message.from_group()} from_self:{message.from_self()} is_text:{message.is_text()} xml:{formatted_xml}"
    return formatted

def wxmsg_to_dict(message: wxmsg.WxMsg) -> dict:
    """
    Convert the received message to a dictionary.
    :param recv: The received message.
    :return: The dictionary.
    """
    dictionary =  {
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
