#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import schedule

from utils.database import BotDatabase
from utils.plans_interface import PlansInterface
from utils.web_api_data import WebApiData


class web_api_data(PlansInterface):
    def __init__(self):
        self.web_api_data = WebApiData()
        self.db = BotDatabase()

    def web_api_data_flush(self):
        self.web_api_data.flush()

    def web_api_data_user_count(self):
        self.web_api_data.update_data('user_count', self.db.get_user_count())

    def web_api_data_running_days(self):
        self.web_api_data.update_data('running_days', self.web_api_data.get_data()['running_days'] + 1)

    def run(self):
        schedule.every(30).seconds.do(self.web_api_data_flush)
        schedule.every(30).seconds.do(self.web_api_data_user_count)
        schedule.every(24).hours.do(self.web_api_data_running_days)
