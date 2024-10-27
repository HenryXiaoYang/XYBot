#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import re

import yaml
from loguru import logger
from wcferry import client

from utils.plugin_interface import PluginInterface
from utils.plugin_manager import plugin_manager
from wcferry_helper import XYBotWxMsg


class manage_plugins(PluginInterface):
    def __init__(self):
        config_path = "plugins/command/manage_plugins.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.load_sub_keywords = config['load_sub_keywords']
        self.unload_sub_keywords = config['unload_sub_keywords']
        self.reload_sub_keywords = config['reload_sub_keywords']
        self.list_sub_keywords = config['list_sub_keywords']

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.admin_list = main_config["admins"]  # 获取管理员列表

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        recv.content = re.split(" |\u2005", recv.content)  # 拆分消息

        admin_wxid = recv.sender  # 获取发送者wxid

        if admin_wxid in self.admin_list:  # 判断是否为管理员
            action = recv.content[1]  # 获取操作名

            if action in self.load_sub_keywords:  # 如果操作为加载，则调用插件管理器加载插件
                await self.load_plugin(bot, recv)

            elif action in self.unload_sub_keywords:  # 如果操作为卸载，则调用插件管理器卸载插件
                await self.unload_plugin(bot, recv)

            elif action in self.reload_sub_keywords:  # 如果操作为重载，则调用插件管理器重载插件
                await self.reload_plugin(bot, recv)

            elif action in self.list_sub_keywords:  # 如果操作为列表，则调用插件管理器获取插件列表
                await self.list_plugins(bot, recv)

            else:  # 操作不存在，则响应错误
                out_message = "-----XYBot-----\n⚠️该操作不存在！"
                logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
                bot.send_text(out_message, recv.roomid)


        else:  # 操作人不在白名单内
            out_message = "-----XYBot-----\n❌你配用这个指令吗？"
            logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid)

    async def load_plugin(self, bot: client.Wcf, recv: XYBotWxMsg):
        try:
            action_plugin = recv.content[2]  # 获取插件名

            if action_plugin == 'manage_plugins':
                out_message = "-----XYBot-----\n❌不能加载该插件！"
                logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
                bot.send_text(out_message, recv.roomid)

            elif action_plugin == '*':
                status = plugin_manager.load_plugins()
                if status[0]:  # 判断是否成功并发送响应
                    out_message = f"-----XYBot-----\n加载所有插件成功！✅\n{status[1]}"
                    logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
                    bot.send_text(out_message, recv.roomid)
                else:
                    out_message = f"-----XYBot-----\n加载所有插件失败！❌\n{status[1]}"
                    logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
                    bot.send_text(out_message, recv.roomid)

            else:
                status = plugin_manager.load_plugin(action_plugin)  # 判断是否成功并发送响应
                if status[0]:  # 判断是否成功并发送响应
                    out_message = f"-----XYBot-----\n加载插件{action_plugin}成功！✅\n{status[1]}"
                    logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
                    bot.send_text(out_message, recv.roomid)
                else:
                    out_message = f"-----XYBot-----\n加载插件{action_plugin}失败！❌\n{status[1]}"
                    logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
                    bot.send_text(out_message, recv.roomid)

        except Exception as error:
            out_message = f"-----XYBot-----\n加载插件失败！❌\n{error}"
            logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid)

    async def unload_plugin(self, bot: client.Wcf, recv: XYBotWxMsg):
        try:
            action_plugin = recv.content[2]  # 获取插件名

            if action_plugin == 'manage_plugins':
                out_message = "-----XYBot-----\n❌不能卸载该插件！"
                logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
                bot.send_text(out_message, recv.roomid)

            elif action_plugin == '*':
                status = plugin_manager.unload_plugins()
                if status[0]:  # 判断是否成功并发送响应
                    out_message = f"-----XYBot-----\n卸载所有插件成功！✅\n{status[1]}"
                    logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
                    bot.send_text(out_message, recv.roomid)
                else:
                    out_message = f"-----XYBot-----\n卸载所有插件失败！❌\n{status[1]}"
                    logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
                    bot.send_text(out_message, recv.roomid)

            else:
                status = plugin_manager.unload_plugin(action_plugin)
                if status[0]:  # 判断是否成功并发送响应
                    out_message = f"-----XYBot-----\n卸载插件{action_plugin}成功！✅\n{status[1]}"
                    logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
                    bot.send_text(out_message, recv.roomid)

                else:
                    out_message = f"-----XYBot-----\n卸载插件{action_plugin}失败！❌\n{status[1]}"
                    logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
                    bot.send_text(out_message, recv.roomid)

        except Exception as error:
            out_message = f"-----XYBot-----\n卸载插件失败！❌\n{error}"
            logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid)

    async def reload_plugin(self, bot: client.Wcf, recv: XYBotWxMsg):
        try:
            action_plugin = recv.content[2]  # 获取插件名

            if action_plugin == 'manage_plugins':
                out_message = "-----XYBot-----\n❌不能重载该插件！"
                logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
                bot.send_text(out_message, recv.roomid)

            elif action_plugin == '*':
                status = plugin_manager.reload_plugins()
                if status[0]:
                    out_message = f"-----XYBot-----\n重载所有插件成功！✅\n{status[1]}"
                    logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
                    bot.send_text(out_message, recv.roomid)
                else:
                    out_message = f"-----XYBot-----\n重载所有插件失败！❌\n{status[1]}"
                    logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
                    bot.send_text(out_message, recv.roomid)

            else:
                status = plugin_manager.reload_plugin(action_plugin)
                if status[0]:  # 判断是否成功并发送响应
                    out_message = f"-----XYBot-----\n重载插件{action_plugin}成功！✅\n{status[1]}"
                    logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
                    bot.send_text(out_message, recv.roomid)
                else:
                    out_message = f"-----XYBot-----\n重载插件{action_plugin}失败！❌\n{status[1]}"
                    logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
                    bot.send_text(out_message, recv.roomid)

        except Exception as error:
            out_message = f"-----XYBot-----\n重载插件失败！❌\n{error}"
            logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid)

    async def list_plugins(self, bot: client.Wcf, recv: XYBotWxMsg):
        out_message = "-----XYBot-----\n已加载插件列表："
        for type in plugin_manager.all_plugin_types:
            for plugin in plugin_manager.plugins[type]:
                out_message += f"\n{plugin}"
        logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
        bot.send_text(out_message, recv.roomid)
