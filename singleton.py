#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.
#
#  This program is licensed under the GNU General Public License v3.0.
def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]

    return inner
