import yaml
from loguru import logger

import pywxdll
from utils.plugin_interface import PluginInterface
from utils.plugin_manager import plugin_manager


class manage_plugins(PluginInterface):
    def __init__(self):
        config_path = "plugins/manage_plugins.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.load_sub_keywords = config['load_sub_keywords']
        self.unload_sub_keywords = config['unload_sub_keywords']
        self.reload_sub_keywords = config['reload_sub_keywords']
        self.list_sub_keywords = config['list_sub_keywords']

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config["ip"]  # 机器人ip
        self.port = main_config["port"]  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

        self.admin_list = main_config["admins"]  # 获取管理员列表

    async def run(self, recv):
        if recv["id1"]:  # 用于判断是否为管理员
            admin_wxid = recv["id1"]  # 是群
        else:
            admin_wxid = recv["wxid"]  # 是私聊

        if admin_wxid in self.admin_list:  # 判断是否为管理员
            action = recv["content"][1]  # 获取操作名

            if action in self.load_sub_keywords:  # 如果操作为加载，则调用插件管理器加载插件
                self.load_plugin(recv)

            elif action in self.unload_sub_keywords:  # 如果操作为卸载，则调用插件管理器卸载插件
                self.unload_plugin(recv)


            elif action in self.reload_sub_keywords:  # 如果操作为重载，则调用插件管理器重载插件
                self.reload_plugin(recv)


            elif action in self.list_sub_keywords:  # 如果操作为列表，则调用插件管理器获取插件列表
                self.list_plugins(recv)

            else:  # 操作不存在，则响应错误
                out_message = "-----XYBot-----\n⚠️该操作不存在！"
                logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
                self.bot.send_txt_msg(recv["wxid"], out_message)


        else:  # 操作人不在白名单内
            out_message = "-----XYBot-----\n❌你配用这个指令吗？"
            logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
            self.bot.send_txt_msg(recv["wxid"], out_message)

    def load_plugin(self, recv):
        action_plugin = recv["content"][2]  # 获取插件名

        if action_plugin == 'manage_plugins':
            out_message = "-----XYBot-----\n❌不能加载该插件！"
            logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
            self.bot.send_txt_msg(recv["wxid"], out_message)
        elif action_plugin == '*':
            if plugin_manager.load_plugins():
                out_message = "-----XYBot-----\n加载所有插件成功！✅"
                logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
                self.bot.send_txt_msg(recv["wxid"], out_message)
        else:
            if plugin_manager.load_plugin(action_plugin):  # 判断是否成功并发送响应
                out_message = f"-----XYBot-----\n加载插件{action_plugin}成功！✅"
                logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
                self.bot.send_txt_msg(recv["wxid"], out_message)

            else:
                out_message = f"-----XYBot-----\n加载插件{action_plugin}失败！❌"
                logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
                self.bot.send_txt_msg(recv["wxid"], out_message)

    def unload_plugin(self, recv):
        action_plugin = recv["content"][2]  # 获取插件名

        if action_plugin == 'manage_plugins':
            out_message = "-----XYBot-----\n❌不能卸载该插件！"
            logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
            self.bot.send_txt_msg(recv["wxid"], out_message)
        elif action_plugin == '*':
            if plugin_manager.unload_plugins():
                out_message = "-----XYBot-----\n卸载所有插件成功！✅"
                logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
                self.bot.send_txt_msg(recv["wxid"], out_message)
        else:
            if plugin_manager.unload_plugin(
                    action_plugin
            ):  # 判断是否成功并发送响应
                out_message = f"-----XYBot-----\n卸载插件{action_plugin}成功！✅"
                logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
                self.bot.send_txt_msg(recv["wxid"], out_message)

            else:
                out_message = f"-----XYBot-----\n卸载插件{action_plugin}失败！❌"
                logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
                self.bot.send_txt_msg(recv["wxid"], out_message)

    def reload_plugin(self, recv):
        action_plugin = recv["content"][2]  # 获取插件名

        if action_plugin == 'manage_plugins':
            out_message = "-----XYBot-----\n❌不能重载该插件！"
            logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
            self.bot.send_txt_msg(recv["wxid"], out_message)
        elif action_plugin == '*':
            if plugin_manager.reload_plugins():
                out_message = "-----XYBot-----\n重载所有插件成功！✅"
                logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
                self.bot.send_txt_msg(recv["wxid"], out_message)
        else:
            if plugin_manager.reload_plugin(
                    action_plugin
            ):  # 判断是否成功并发送响应
                out_message = f"-----XYBot-----\n重载插件{action_plugin}成功！✅"
                logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
                self.bot.send_txt_msg(recv["wxid"], out_message)

            else:
                out_message = f"-----XYBot-----\n重载插件{action_plugin}失败！❌"
                logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
                self.bot.send_txt_msg(recv["wxid"], out_message)

    def list_plugins(self, recv):
        out_message = "-----XYBot-----\n已加载插件列表："
        for plugin in plugin_manager.plugins.keys():
            out_message += f"\n{plugin}"
        logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
        self.bot.send_txt_msg(recv["wxid"], out_message)  # 发送插件列表
