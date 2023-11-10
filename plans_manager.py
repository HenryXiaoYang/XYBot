import importlib
import os

from plans_interface import PlansInterface


class PlansManager:
    def __init__(self):
        self.plans = {}

    def load_plan(self, plan_name):
        if plan_name not in self.plans:
            module = importlib.import_module(f'plans.{plan_name}')
            plan_class = getattr(module, plan_name)
            if issubclass(plan_class, PlansInterface):
                plan_cinstance = plan_class()
                self.plans[plan_name] = plan_cinstance
            self.plans[plan_name].run()

    def load_plans(self, plan_dir):
        for plan_file in os.listdir(plan_dir):
            if plan_file.endswith(".py") and plan_file != "__init__.py" and not plan_file.startswith('_'):
                plan_name = os.path.splitext(plan_file)[0]
                self.load_plan(plan_name)

    def unload_plan(self, plan_name):
        if plan_name in self.plans:
            del self.plans[plan_name]


# 实例化插件管理器
plan_manager = PlansManager()
