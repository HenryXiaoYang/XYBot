import os

import pywxdll
import yaml
from loguru import logger

import plugin_manager
from plugin_interface import PluginInterface
from plugin_manager import plugin_manager


class manage_plugins(PluginInterface):
    def __init__(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.load(f.read(), Loader=yaml.FullLoader)

        self.ip = main_config['ip']
        self.port = main_config['port']
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

        self.admin_list = main_config['admins']

    def run(self, recv):
        if recv['id1']:  # 用于判断是否为管理员
            admin_wxid = recv['id1']  # 是群
        else:
            admin_wxid = recv['wxid']  # 是私聊

        if admin_wxid in self.admin_list:
            action = recv['content'][1]

            if action in ['加载', 'load']:
                action_plugin = recv['content'][2]

                if plugin_manager.load_plugin(action_plugin):
                    out_message = '-----XYBot-----\n加载插件{action_plugin}成功！✅'.format(action_plugin=action_plugin)
                    logger.info(
                        '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
                    self.bot.send_txt_msg(recv['wxid'], out_message)
                else:
                    out_message = '-----XYBot-----\n加载插件{action_plugin}失败！❌'.format(action_plugin=action_plugin)
                    logger.info(
                        '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
                    self.bot.send_txt_msg(recv['wxid'], out_message)
            elif action in ['卸载', 'unload']:
                action_plugin = recv['content'][2]

                if plugin_manager.unload_plugin(action_plugin):
                    out_message = '-----XYBot-----\n卸载插件{action_plugin}成功！✅'.format(action_plugin=action_plugin)
                    logger.info(
                        '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
                    self.bot.send_txt_msg(recv['wxid'], out_message)
                else:
                    out_message = '-----XYBot-----\n卸载插件{action_plugin}失败！❌'.format(action_plugin=action_plugin)
                    logger.info(
                        '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
                    self.bot.send_txt_msg(recv['wxid'], out_message)

            elif action in ['重载', 'reload']:
                action_plugin = recv['content'][2]

                if plugin_manager.reload_plugin(action_plugin):
                    out_message = '-----XYBot-----\n重载插件{action_plugin}成功！✅'.format(action_plugin=action_plugin)
                    logger.info(
                        '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
                    self.bot.send_txt_msg(recv['wxid'], out_message)
                else:
                    out_message = '-----XYBot-----\n重载插件{action_plugin}失败！❌'.format(action_plugin=action_plugin)
                    logger.info(
                        '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
                    self.bot.send_txt_msg(recv['wxid'], out_message)

            elif action in ['列表', 'list']:
                out_message = '-----XYBot-----\n已加载插件列表：'
                for plugin in plugin_manager.plugins.keys():
                    out_message += '\n{plugin}'.format(plugin=plugin)
                logger.info(
                    '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
                self.bot.send_txt_msg(recv['wxid'], out_message)
            else:
                out_message = '-----XYBot-----\n⚠️该操作不存在！'
                logger.info(
                    '[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
                self.bot.send_txt_msg(recv['wxid'], out_message)


        else:  # 操作人不在白名单内
            out_message = '-----XYBot-----\n❌你配用这个指令吗？'
            logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
            self.bot.send_txt_msg(recv['wxid'], out_message)
