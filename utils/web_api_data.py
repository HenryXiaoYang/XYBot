#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.
import json
import os

from utils.singleton import singleton


@singleton
class WebApiData:
    def __init__(self):
        file_path = 'resources/web_api_data.json'
        default_data = {
            "received_message_count": 0,
            "sent_message_count": 0,
            "user_count": 0,
            "running_days": 0
        }

        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                self.data = json.load(f)
        else:
            with open(file_path, 'w') as f:
                json.dump(default_data, f)
            self.data = default_data

    def get_data(self):
        return self.data

    def update_data(self, key, value):
        if key in self.data:
            self.data[key] = value

    def flush(self):
        file_path = 'resources/web_api_data.json'
        if os.path.exists(file_path):
            with open(file_path, 'r+') as f:
                json.dump(self.get_data(), f)
                f.truncate()
