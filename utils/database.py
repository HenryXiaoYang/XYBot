#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor

from loguru import logger

from utils.singleton import singleton


# 2b queue没法获取返回值


@singleton
class BotDatabase:
    def __init__(self):
        if not os.path.exists("userpoints.db"):  # 检查数据库是否存在
            logger.warning("监测到数据库不存在，正在创建数据库")
            conn = sqlite3.connect("userpoints.db")
            c = conn.cursor()
            c.execute(
                """CREATE TABLE USERPOINTS (WXID TEXT PRIMARY KEY , POINTS INT, SIGNINSTAT INT, WHITELIST INT)"""
            )
            conn.commit()
            c.close()
            conn.close()
            logger.warning("已创建数据库")

        self.database = sqlite3.connect(
            "userpoints.db", check_same_thread=False
        )  # 连接数据库
        self.wxid_list = self._get_wxid_list()  # 获取已有用户列表

        self.executor = ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="database"
        )  # 用来当queue用

    def _execute_in_queue(self, method, *args, **kwargs):
        future = self.executor.submit(method, *args, **kwargs)

        try:
            return future.result(timeout=20)
        except Exception as error:
            # 处理异常情况
            logger.error(error)

    def _get_wxid_list(self):
        cursor = self.database.cursor()

        try:
            cursor.execute("select u.WXID from USERPOINTS u;")  # 获取已有用户列表
            return cursor.fetchall()
        finally:
            cursor.close()

    def _check_user(self, wxid):
        cursor = self.database.cursor()
        try:
            if not (wxid,) in self.wxid_list:  # 不存在，创建用户并设置积分为增加的积分
                sql_command = "INSERT INTO USERPOINTS VALUES {}".format((wxid, 0, 0, 0))
                cursor.execute(sql_command)
                self.database.commit()  # 提交数据库
            cursor.execute("select u.WXID from USERPOINTS u;")  # 刷新已有用户列表
            self.wxid_list = cursor.fetchall()  # 刷新已有用户列表
        finally:
            cursor.close()

    def add_points(self, wxid, num):
        return self._execute_in_queue(self._add_points, wxid, num)

    def _add_points(self, wxid, num):
        cursor = self.database.cursor()

        try:
            self._check_user(wxid)
            sql_command = "SELECT POINTS FROM USERPOINTS WHERE WXID='{wxid}'".format(
                wxid=wxid
            )
            cursor.execute(sql_command)
            new_points = cursor.fetchall()[0][0] + num
            sql_command = (
                "UPDATE USERPOINTS SET POINTS={point} WHERE WXID='{wxid}'".format(
                    point=new_points, wxid=wxid
                )
            )
            cursor.execute(sql_command)
            self.database.commit()
        finally:
            cursor.close()

    def set_points(self, wxid, num):
        return self._execute_in_queue(self._set_points, wxid, num)

    def _set_points(self, wxid, num):
        cursor = self.database.cursor()

        try:
            self._check_user(wxid)
            sql_command = (
                "UPDATE USERPOINTS SET POINTS={point} WHERE WXID='{wxid}'".format(
                    point=num, wxid=wxid
                )
            )
            cursor.execute(sql_command)
            self.database.commit()
        finally:
            cursor.close()

    def get_points(self, wxid):
        return self._execute_in_queue(self._get_points, wxid)

    def _get_points(self, wxid):
        cursor = self.database.cursor()

        try:
            self._check_user(wxid)
            sql_command = "SELECT POINTS FROM USERPOINTS WHERE WXID='{wxid}'".format(
                wxid=wxid
            )
            cursor.execute(sql_command)
            result = cursor.fetchall()[0][0]
            return result
        finally:
            cursor.close()

    def get_stat(self, wxid):
        return self._execute_in_queue(self._get_stat, wxid)

    def _get_stat(self, wxid):
        cursor = self.database.cursor()

        try:
            self._check_user(wxid)
            sql_command = (
                "SELECT SIGNINSTAT FROM USERPOINTS WHERE WXID='{wxid}'".format(
                    wxid=wxid
                )
            )
            cursor.execute(sql_command)
            result = cursor.fetchall()[0][0]
            return result
        finally:
            cursor.close()

    def set_stat(self, wxid, num):
        return self._execute_in_queue(self._set_stat, wxid, num)

    def _set_stat(self, wxid, num):
        cursor = self.database.cursor()

        try:
            self._check_user(wxid)
            sql_command = "UPDATE USERPOINTS SET SIGNINSTAT={SIGNINSTAT} WHERE WXID='{wxid}'".format(
                SIGNINSTAT=num, wxid=wxid
            )
            cursor.execute(sql_command)
            self.database.commit()  # 提交数据库
        finally:
            cursor.close()

    def reset_stat(self):
        return self._execute_in_queue(self._reset_stat)

    def _reset_stat(self):
        cursor = self.database.cursor()

        try:
            sql_command = "UPDATE USERPOINTS SET SIGNINSTAT=0"
            cursor.execute(sql_command)
            self.database.commit()  # 提交数据库
        finally:
            cursor.close()

    def get_highest_points(self, num):
        return self._execute_in_queue(self._get_highest_points, num)

    def _get_highest_points(self, num):
        cursor = self.database.cursor()

        try:
            sql_command = "select * from USERPOINTS order by POINTS DESC, SIGNINSTAT LIMIT 0,{limit}".format(
                limit=num
            )
            cursor.execute(sql_command)
            result = cursor.fetchall()
            return result
        finally:
            cursor.close()

    def set_whitelist(self, wxid, stat):
        return self._execute_in_queue(self._set_whitelist, wxid, stat)

    def _set_whitelist(self, wxid, stat):
        cursor = self.database.cursor()

        try:
            self._check_user(wxid)
            sql_command = "UPDATE USERPOINTS SET WHITELIST={whitelist} WHERE WXID='{wxid}'".format(
                whitelist=stat, wxid=wxid
            )
            cursor.execute(sql_command)
            self.database.commit()  # 提交数据库
        finally:
            cursor.close()

    def get_whitelist(self, wxid):
        return self._execute_in_queue(self._get_whitelist, wxid)

    def _get_whitelist(self, wxid):
        cursor = self.database.cursor()

        try:
            self._check_user(wxid)
            sql_command = "SELECT WHITELIST FROM USERPOINTS WHERE WXID='{wxid}'".format(
                wxid=wxid
            )
            cursor.execute(sql_command)
            result = cursor.fetchall()[0][0]
            return result
        finally:
            cursor.close()

    def safe_trade_points(self, trader_wxid, target_wxid, num):
        return self._execute_in_queue(
            self._safe_trade_points, trader_wxid, target_wxid, num
        )

    def _safe_trade_points(self, trader_wxid, target_wxid, num):
        cursor = self.database.cursor()

        try:
            self._check_user(trader_wxid)
            self._check_user(target_wxid)
            get_trader_point_sql_command = (
                "SELECT POINTS FROM USERPOINTS WHERE WXID='{wxid}'".format(
                    wxid=trader_wxid
                )
            )
            cursor.execute(get_trader_point_sql_command)
            trader_points = cursor.fetchall()[0][0]
            if trader_points >= num:
                self._add_points(trader_wxid, num * -1)
                self._add_points(target_wxid, num)
                return True
            else:
                return False
        finally:
            cursor.close()

    def get_user_list(self) -> list:
        return self._execute_in_queue(self._get_user_list)

    def _get_user_list(self) -> list:
        cursor = self.database.cursor()

        try:
            cursor.execute("select * from USERPOINTS")
            result = cursor.fetchall()
            return result
        finally:
            cursor.close()

    def get_user_count(self) -> int:
        return self._execute_in_queue(self._get_user_count)

    def _get_user_count(self) -> int:
        cursor = self.database.cursor()

        try:
            cursor.execute("select count(*) from USERPOINTS")
            result = cursor.fetchall()[0][0]
            return result
        finally:
            cursor.close()
