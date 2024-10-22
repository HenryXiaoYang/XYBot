#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import importlib
import os

from loguru import logger
from wcferry import client

from utils.plans_interface import PlansInterface
from utils.singleton import singleton


@singleton
class PlansManager:
    def __init__(self):
        self.plans = {}

    def load_plan(self, bot: client.Wcf, plan_name):
        if plan_name not in self.plans:
            module = importlib.import_module(f"plans.{plan_name}")
            plan_class = getattr(module, plan_name)
            if issubclass(plan_class, PlansInterface):
                plan_cinstance = plan_class()
                self.plans[plan_name] = plan_cinstance
                self.plans[plan_name].run(bot)
                logger.info(f"+ 已加载计划：{plan_name}")
            else:
                logger.error(f"计划{plan_name}不是PlansInterface的子类")

    def load_plans(self, bot: client.Wcf, plan_dir):
        logger.info("开始加载所有计划")
        for plan_file in os.listdir(plan_dir):
            if plan_file.endswith(".py") and plan_file != "__init__.py" and not plan_file.startswith("_"):
                plan_name = os.path.splitext(plan_file)[0]
                self.load_plan(bot, plan_name)

    def unload_plan(self, plan_name):
        if plan_name in self.plans:
            del self.plans[plan_name]
            logger.info(f"- 已卸载计划{plan_name}")


# 实例化插件管理器
plan_manager = PlansManager()
