#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import importlib
import os
import sys

import yaml
from loguru import logger

from utils.plugin_interface import PluginInterface
from utils.singleton import singleton


@singleton
class PluginManager:
    def __init__(self):
        self.plugins = {"command": {}, "text": {}, "mention": {}, "image": {}, "voice": {}, "join_group": {}}
        self.keywords = {}

        with open("main_config.yml", "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.excluded_plugins = config["excluded_plugins"]

        self.all_plugin_types = ["command", "text", "mention", "image", "voice", "join_group"]

    def refresh_keywords(self):
        """
        刷新关键词。Refresh the keywords.
        :return: (bool, str) - 如果刷新成功，返回True和成功消息。如果刷新失败，返回False和失败原因 (bool, str) - True and a success message if the keywords were refreshed successfully, False and an error message otherwise.
        """
        self.keywords.clear()
        plugins_folder = "plugins/command"

        # 遍历文件夹中的所有文件
        for root, dirs, files in os.walk(plugins_folder):
            for file in files:
                if file.endswith(".yml") and not file.startswith("_"):
                    # 处理符合条件的文件
                    file_path = os.path.join(root, file)

                    with open(file_path, "r", encoding="utf-8") as f:  # 读取设置
                        config = yaml.safe_load(f.read())

                    keywords_list = config["keywords"]
                    plugin_name = config["plugin_name"]

                    if plugin_name in self.plugins["command"].keys():
                        for keyword in keywords_list:
                            self.keywords[keyword] = plugin_name

        logger.info("已刷新指令关键词")
        return True, "成功"

    def get_keywords(self):
        return self.keywords

    def load_plugin(self, plugin_name: str, no_refresh: bool = False, log: bool = True):
        """
        按插件名称加载插件。插件必须是PluginInterface的子类。
        Loads a plugin by its name. The plugin must be a subclass of PluginInterface.

        :param plugin_name: 要加载的插件的名称。The name of the plugin to load.
        :param no_refresh: 是否刷新关键词。Whether to refresh the keywords.
        :param log: 是否进行日志。Whether to log.
        :return: tuple -(bool, str) - 如果加载成功，返回True和成功消息。如果加载失败，返回False和失败原因 (bool, str) - True and a success message if the plugin was loaded successfully, False and an error message otherwise.
        """
        if plugin_name in self.plugins:
            logger.warning(f"! 未加载插件：{plugin_name}，因为它已经加载")
            return False, f"插件 {plugin_name} 已经加载。"

        for plugin_type in self.all_plugin_types:  # 遍历所有插件文件夹
            if f"{plugin_name}.py" in os.listdir(f'plugins/{plugin_type}'):  # 判断插件是否存在
                module = importlib.import_module(f"plugins.{plugin_type}.{plugin_name}")  # 导入插件
                plugin_class = getattr(module, plugin_name)  # 获取插件类
                if issubclass(plugin_class, PluginInterface):  # 判断插件是否是PluginInterface的子类
                    plugin_instance = plugin_class()
                    self.plugins[plugin_type][plugin_name] = plugin_instance  # 将插件实例存入插件字典
                    if log:
                        logger.info(f"+ 已加载插件：{plugin_name}")
                    if not no_refresh:
                        self.refresh_keywords()
                    return True, "成功"  # 如果插件加载成功则返回True

                else:
                    logger.warning(f"! 未加载插件：{plugin_name}，因为它不是PluginInterface的子类")
                    return False, f"插件 {plugin_name} 不是 PluginInterface 的子类。"

        logger.warning(f"! 未加载插件：{plugin_name}，因为它不存在")
        return False, f"插件 {plugin_name} 不存在。"

    def load_plugins(self):
        """
        加载所有插件。Load all plugins.
        :return: (bool, str) - 如果加载成功，返回True和成功消息。如果加载失败，返回False和失败原因 (bool, str) - True and a success message if the plugins were loaded successfully, False and an error message otherwise.
        """
        logger.info("开始加载所有插件")

        for plugin_type in self.all_plugin_types:
            for plugin_file in os.listdir(f"plugins/{plugin_type}"):
                if plugin_file.endswith(".py") and not plugin_file.startswith("_"):
                    plugin_name = os.path.splitext(plugin_file)[0]

                    if plugin_name in self.excluded_plugins:
                        logger.info(f"! 未加载插件：{plugin_name}，因为它在排除列表中")

                    else:
                        module = importlib.import_module(f"plugins.{plugin_type}.{plugin_name}")  # 导入插件
                        plugin_class = getattr(module, plugin_name)  # 获取插件类
                        if issubclass(plugin_class, PluginInterface):  # 判断插件是否是PluginInterface的子类
                            plugin_instance = plugin_class()
                            self.plugins[plugin_type][plugin_name] = plugin_instance  # 将插件实例存入插件字典
                            logger.info(f"+ 已加载插件：{plugin_name}")

                        else:
                            logger.error(f"! 未加载插件：{plugin_name}，因为它不是PluginInterface的子类")

        self.refresh_keywords()
        return True, "成功"

    def unload_plugin(self, plugin_name, no_refresh: bool = False):
        """
        卸载插件。Unload a plugin.
        :param plugin_name: 插件名。The name of the plugin to unload.
        :param no_refresh: 是否刷新关键词。Whether to refresh the keywords.
        :return: tuple -(bool, str) - 如果卸载成功，返回True和成功消息。如果卸载失败，返回False和失败原因 (bool, str) - True and a success message if the plugin was unloaded successfully, False and an error message otherwise.
        """
        for plugin_type in self.all_plugin_types:
            if plugin_name in list(self.plugins[plugin_type].keys()):
                del self.plugins[plugin_type][plugin_name]
                del sys.modules[f"plugins.{plugin_type}.{plugin_name}"]
                logger.info(f"- 已卸载插件：{plugin_name}")
                if not no_refresh:
                    self.refresh_keywords()
                return True, "成功"  # 如果插件卸载成功则返回True
        logger.info(f"! 未找到插件：{plugin_name}，无法卸载")
        return False, f"未找到插件：{plugin_name}"  # 如果插件不存在则返回False

    def unload_plugins(self):
        """
        卸载所有插件。Unload all plugins.
        :return: tuple -(bool, str) - 如果卸载成功，返回True和成功消息。如果卸载失败，返回False和失败原因 (bool, str) - True and a success message if the plugins were unloaded successfully, False and an error message otherwise.
        """
        logger.info("开始卸载所有插件")
        for plugin_type in self.all_plugin_types:
            for plugin_name in list(self.plugins[plugin_type].keys()):
                if plugin_name != "manage_plugins":
                    del self.plugins[plugin_type][plugin_name]
                    del sys.modules[f"plugins.{plugin_type}.{plugin_name}"]
                    logger.info(f"- 已卸载插件：{plugin_name}")
        self.refresh_keywords()
        return True, "成功"

    def reload_plugin(self, plugin_name):
        """
        重载插件。Reload a plugin.
        :param plugin_name: 插件名。The name of the plugin to reload.
        :return: (bool, str) - 如果重载成功，返回True和成功消息。如果重载失败，返回False和失败原因 (bool, str) - True and a success message if the plugin was reloaded successfully, False and an error message otherwise.
        """
        if plugin_name == "manage_plugins":
            logger.info("! 禁止重载插件：manage_plugins")
            return False, "禁止重载manage_plugins"

        for plugin_type in self.all_plugin_types:
            if plugin_name in list(self.plugins[plugin_type].keys()):
                # 卸载
                del self.plugins[plugin_type][plugin_name]
                del sys.modules[f"plugins.{plugin_type}.{plugin_name}"]

                # 加载
                module = importlib.import_module(f"plugins.{plugin_type}.{plugin_name}")  # 导入插件
                plugin_class = getattr(module, plugin_name)  # 获取插件类
                if issubclass(plugin_class, PluginInterface):  # 判断插件是否是PluginInterface的子类
                    plugin_instance = plugin_class()
                    self.plugins[plugin_type][plugin_name] = plugin_instance  # 将插件实例存入插件字典

                    self.refresh_keywords()
                    logger.info(f"+ 已重载插件：{plugin_name}")
                    return True, "成功"

                else:
                    logger.error(f"! 未重载插件：{plugin_name}，因为它不是PluginInterface的子类")
                    return False, f"插件 {plugin_name} 不是 PluginInterface 的子类。"

        logger.error(f"! 未重载插件：{plugin_name}，因为它不存在")
        return False, f"插件 {plugin_name} 不存在。"

    def reload_plugins(self):
        """
        重载所有插件。Reload all plugins.
        :return: (bool, str) - 如果重载成功，返回True和成功消息。如果重载失败，返回False和失败原因 (bool, str) - True and a success message if the plugins were reloaded successfully, False and an error message otherwise.
        """
        logger.info("开始重载所有插件")
        for plugin_type in self.all_plugin_types:
            for plugin_name in list(self.plugins[plugin_type].keys()):
                if plugin_name != "manage_plugins":
                    # 卸载
                    del self.plugins[plugin_type][plugin_name]
                    del sys.modules[f"plugins.{plugin_type}.{plugin_name}"]

                    # 加载
                    module = importlib.import_module(f"plugins.{plugin_type}.{plugin_name}")
                    plugin_class = getattr(module, plugin_name)
                    if issubclass(plugin_class, PluginInterface):
                        plugin_instance = plugin_class()
                        self.plugins[plugin_type][plugin_name] = plugin_instance
                        logger.info(f"+ 已重载插件：{plugin_name}")
                    else:
                        logger.error(f"! 未重载插件：{plugin_name}，因为它不是PluginInterface的子类")
        return True, "成功"


# 实例化插件管理器
plugin_manager = PluginManager()
