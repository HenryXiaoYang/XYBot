import yaml
from loguru import logger

import pywxdll
from utils.plugin_interface import PluginInterface
from utils.plugin_manager import plugin_manager


class manage_plugins(PluginInterface):
    def __init__(self):
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

            if action in ["加载", "load"]:  # 如果操作为加载，则调用插件管理器加载插件
                action_plugin = recv["content"][2]  # 获取插件名

                if plugin_manager.load_plugin(action_plugin):  # 判断是否成功并发送响应
                    out_message = f"-----XYBot-----\n加载插件{action_plugin}成功！✅"
                    logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
                    self.bot.send_txt_msg(recv["wxid"], out_message)

                else:
                    out_message = f"-----XYBot-----\n加载插件{action_plugin}失败！❌"
                    logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
                    self.bot.send_txt_msg(recv["wxid"], out_message)

            elif action in [
                "卸载",
                "unload",
            ]:  # 如果操作为卸载，则调用插件管理器卸载插件
                action_plugin = recv["content"][2]  # 获取插件名

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


            elif action in [
                "重载",
                "reload",
            ]:  # 如果操作为重载，则调用插件管理器重载插件
                action_plugin = recv["content"][2]  # 获取插件名

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


            elif action in [
                "列表",
                "list",
            ]:  # 如果操作为列表，则调用插件管理器获取插件列表
                out_message = "-----XYBot-----\n已加载插件列表："
                for plugin in plugin_manager.plugins.keys():
                    out_message += f"\n{plugin}"
                logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
                self.bot.send_txt_msg(recv["wxid"], out_message)  # 发送插件列表

            else:  # 操作不存在，则响应错误
                out_message = "-----XYBot-----\n⚠️该操作不存在！"
                logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
                self.bot.send_txt_msg(recv["wxid"], out_message)


        else:  # 操作人不在白名单内
            out_message = "-----XYBot-----\n❌你配用这个指令吗？"
            logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
            self.bot.send_txt_msg(recv["wxid"], out_message)
