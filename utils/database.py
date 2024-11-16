#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.
import json
import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor

from loguru import logger

from utils.singleton import singleton


# sb queue内置库没法获取返回值

@singleton
class BotDatabase:
    def __init__(self):
        self.database_column = [("WXID", "TEXT PRIMARY KEY"), ("NICKNAME", "TEXT"), ("POINTS", "INT"), ("SIGNINSTAT", "INT"),("WHITELIST", "INT"), ("PRIVATE_GPT_DATA", "TEXT")]

        if not os.path.exists("userdata.db"):  # 检查数据库是否存在
            logger.warning("检测到数据库不存在，正在创建数据库")
            conn = sqlite3.connect("userdata.db")
            c = conn.cursor()

            # compose create table sql
            create_table_sql = f"CREATE TABLE USERDATA ("
            for column in self.database_column:
                create_table_sql += f"{column[0]} {column[1]}, "
            create_table_sql = create_table_sql[:-2] + ")"

            c.execute(create_table_sql)

            conn.commit()
            c.close()
            conn.close()

            logger.warning("已创建数据库")

        self.database = sqlite3.connect(
            "userdata.db", check_same_thread=False
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
            cursor.execute("select u.WXID from USERDATA u;")  # 获取已有用户列表
            return cursor.fetchall()
        finally:
            cursor.close()

    def _check_user(self, wxid):
        cursor = self.database.cursor()
        try:
            if not (wxid,) in self.wxid_list:  # 不存在，创建用户并设置积分为增加的积分
                sql = "INSERT INTO USERDATA (WXID, NICKNAME, POINTS, SIGNINSTAT, WHITELIST, PRIVATE_GPT_DATA) VALUES (?, ?, ?, ?, ?, ?)"
                arg = (wxid, "", 0, 0, 0, "{}")
                cursor.execute(sql, arg)
                self.database.commit()  # 提交数据库
            cursor.execute("select u.WXID from USERDATA u;")  # 刷新已有用户列表
            self.wxid_list = cursor.fetchall()  # 刷新已有用户列表
        finally:
            cursor.close()

    def add_points(self, wxid, num):
        return self._execute_in_queue(self._add_points, wxid, num)

    def _add_points(self, wxid, num):
        cursor = self.database.cursor()

        try:
            self._check_user(wxid)
            sql = "SELECT POINTS FROM USERDATA WHERE WXID=?"  # 获取当前积分
            arg = (wxid,)
            cursor.execute(sql, arg)
            new_points = cursor.fetchall()[0][0] + num
            sql = "UPDATE USERDATA SET POINTS=? WHERE WXID=?"
            arg = (new_points, wxid,)
            cursor.execute(sql, arg)
            self.database.commit()
            logger.info(f"[数据库] {wxid} 积分已加 {num} 点，当前积分{new_points}")
        finally:
            cursor.close()

    def set_points(self, wxid, num):
        return self._execute_in_queue(self._set_points, wxid, num)

    def _set_points(self, wxid, num):
        cursor = self.database.cursor()

        try:
            self._check_user(wxid)
            sql = "UPDATE USERDATA SET POINTS=? WHERE WXID=?"
            arg = (num, wxid,)
            cursor.execute(sql, arg)
            self.database.commit()
            logger.info(f"[数据库] {wxid} 积分已设置为 {num} 点")
        finally:
            cursor.close()

    def get_points(self, wxid):
        return self._execute_in_queue(self._get_points, wxid)

    def _get_points(self, wxid):
        cursor = self.database.cursor()

        try:
            self._check_user(wxid)
            sql = "SELECT POINTS FROM USERDATA WHERE WXID=?"
            arg = (wxid,)
            cursor.execute(sql, arg)
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
            sql = "SELECT SIGNINSTAT FROM USERDATA WHERE WXID=?"
            arg = (wxid,)
            cursor.execute(sql, arg)
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
            sql = "UPDATE USERDATA SET SIGNINSTAT=? WHERE WXID=?"

            arg = (num, wxid,)
            cursor.execute(sql, arg)
            self.database.commit()  # 提交数据库
            logger.info(f"[数据库] {wxid} 签到状态已设置为 {num}")
        finally:
            cursor.close()

    def reset_stat(self):
        cursor = self.database.cursor()

        try:
            sql = "UPDATE USERDATA SET SIGNINSTAT=0"
            cursor.execute(sql)
            self.database.commit()  # 提交数据库
            logger.info("[数据库] 签到状态已重置")
        finally:
            cursor.close()

    def get_highest_points(self, num):
        cursor = self.database.cursor()

        try:
            sql = "SELECT * FROM USERDATA ORDER BY POINTS DESC LIMIT ?;"
            arg = (num,)
            cursor.execute(sql, arg)
            result = cursor.fetchall()
            return result
        finally:
            cursor.close()

    def set_whitelist(self, wxid, stat):
        cursor = self.database.cursor()

        try:
            self._check_user(wxid)
            sql = "UPDATE USERDATA SET WHITELIST=? WHERE WXID=?"
            arg = (stat, wxid,)
            cursor.execute(sql, arg)
            self.database.commit()  # 提交数据库
            logger.info(f"[数据库] {wxid} 白名单状态已设置为 {stat}")
        finally:
            cursor.close()

    def get_whitelist(self, wxid):
        cursor = self.database.cursor()

        try:
            self._check_user(wxid)
            sql = "SELECT WHITELIST FROM USERDATA WHERE WXID=?"
            arg = (wxid,)
            cursor.execute(sql, arg)
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
            sql = "SELECT POINTS FROM USERDATA WHERE WXID=?"
            arg = (trader_wxid,)

            cursor.execute(sql, arg)
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
        cursor = self.database.cursor()

        try:
            cursor.execute("select * from USERDATA")
            result = cursor.fetchall()
            return result
        finally:
            cursor.close()

    def get_user_count(self) -> int:
        cursor = self.database.cursor()

        try:
            cursor.execute("select count(*) from USERDATA")
            result = cursor.fetchall()[0][0]
            return result
        finally:
            cursor.close()

    def get_private_gpt_data(self, wxid: str) -> dict:
        cursor = self.database.cursor()

        try:
            self._check_user(wxid)
            sql = "SELECT PRIVATE_GPT_DATA FROM USERDATA WHERE WXID=?"
            arg = (wxid,)
            cursor.execute(sql, arg)
            json_string = cursor.fetchone()[0]
            if not json_string:
                return {}
            else:
                json_data = json.loads(json_string)
                return json_data
        finally:
            cursor.close()

    def save_private_gpt_data(self, wxid: str, data: dict) -> None:
        cursor = self.database.cursor()

        try:
            self._check_user(wxid)
            json_string = json.dumps(data)

            sql = "UPDATE USERDATA SET PRIVATE_GPT_DATA=? WHERE WXID=?"
            args = (json_string, wxid,)
            cursor.execute(sql, args)
            self.database.commit()  # 提交数据库
            logger.info(f"[数据库] {wxid} 私聊GPT数据已保存")
        finally:
            cursor.close()

    def add_column(self, column_name: str, column_type: str) -> None:
        cursor = self.database.cursor()

        try:
            sql = "ALTER TABLE USERDATA ADD COLUMN ? ?"
            arg = (column_name, column_type,)
            cursor.execute(sql, arg)
            self.database.commit()
            logger.info(f"[数据库] 已添加列 {column_name}")
        finally:
            cursor.close()

    def remove_column(self, column_name: str) -> None:
        cursor = self.database.cursor()

        try:
            sql = "ALTER TABLE USERDATA DROP COLUMN ?"
            arg = (column_name,)
            cursor.execute(sql, arg)
            self.database.commit()
            logger.info(f"[数据库] 已删除列 {column_name}")
        finally:
            cursor.close()

    def get_columns(self) -> list:
        cursor = self.database.cursor()

        try:
            cursor.execute("PRAGMA table_info(USERDATA)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            return column_names
        finally:
            cursor.close()

    def get_nickname(self, wxid: str) -> str:
        cursor = self.database.cursor()

        try:
            self._check_user(wxid)
            sql = "SELECT NICKNAME FROM USERDATA WHERE WXID=?"
            arg = (wxid,)
            cursor.execute(sql, arg)
            result = cursor.fetchall()[0][0]

            return result
        finally:
            cursor.close()

    def set_nickname(self, wxid: str, nickname: str) -> None:
        cursor = self.database.cursor()

        try:
            self._check_user(wxid)
            sql = "UPDATE USERDATA SET NICKNAME=? WHERE WXID=?"

            arg = (nickname, wxid,)
            cursor.execute(sql, arg)
            self.database.commit()  # 提交数据库
        finally:
            cursor.close()
