from loguru import logger
from wcferry import client
from utils.plugin_interface import PluginInterface
from wcferry_helper import XYBotWxMsg
import random
import yaml

class food_selector(PluginInterface):
    def __init__(self):
        config_path = "plugins/command/food_selector.yml"
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f.read())
        
        self.food_options = config["food_options"]
        self.command_format_menu = config["command_format_menu"]

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        selected_food = random.choice(self.food_options)
        message = (
            f"-----XYBot-----\n"
            f"🍽️随机选择的外卖品种是：{selected_food}\n\n"
            f"💝温馨提示：\n"
            f"🌟 记得吃饭要细嚼慢咽哦\n"
            f"🌟 工作再忙也要按时吃饭\n"
            f"🌟 注意营养均衡，保重身体\n"
            f"祝您用餐愉快！😊"
        )
        
        await self.send_friend_or_group(bot, recv, message)
        logger.info(f"[食物选择] wxid: {recv.sender} | 选择结果: {selected_food}")

    async def send_friend_or_group(self, bot: client.Wcf, recv: XYBotWxMsg, out_message="null"):
        if recv.from_group():
            out_message = f"@{recv.sender}\n{out_message}"
            logger.info(f'[发送@信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid, recv.sender)
        else:
            logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid)
