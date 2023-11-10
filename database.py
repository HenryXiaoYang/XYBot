import os
import sqlite3
import threading

lock = threading.Lock()  # sqlite wcnm 天天 Recursive use of cursors not allowed 我直接把你线程全锁了看你咋皮

class BotDatabase:
    _instance = None


    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def __init__(self):
        super().__init__()

        try:  # sqlite wcnm 天天 Recursive use of cursors not allowed 我直接把你线程全锁了看你咋皮
            lock.acquire(True)

            if not os.path.exists('userpoints.db'):  # 检查数据库是否存在
                conn = sqlite3.connect('userpoints.db', check_same_thread=False)
                c = conn.cursor()
                c.execute('CREATE TABLE USERPOINTS (WXID TEXT PRIMARY KEY, POINTS INT, SIGNINSTAT INT, WHITELIST INT)')
                conn.commit()
                c.close()
                conn.close()
            else:
                conn = sqlite3.connect('userpoints.db', check_same_thread=False)
                conn.commit()
                conn.close()

            self.database = sqlite3.connect('userpoints.db', check_same_thread=False)  # 连接数据库
            self.c = self.database.cursor()
            self.c.execute('select u.WXID from USERPOINTS u;')  # 获取已有用户列表
            self.wxid_list = self.c.fetchall()

        finally:
            lock.release()  # 给线程解锁

    def _check_user(self, wxid):
        if not (wxid,) in self.wxid_list:  # 不存在，创建用户并设置积分为增加的积分
            sql_command = "INSERT INTO USERPOINTS VALUES {}".format((wxid, 0, 0, 0))
            self.c.execute(sql_command)
            self.database.commit()  # 提交数据库
        self.c.execute('select u.WXID from USERPOINTS u;')  # 刷新已有用户列表
        self.wxid_list = self.c.fetchall()  # 刷新已有用户列表
        self.database.commit()  # 提交数据库

    def add_points(self, wxid, num):
        try:
            lock.acquire(True)  # 给线程上锁

            self._check_user(wxid)
            sql_command = "SELECT POINTS FROM USERPOINTS WHERE WXID='{wxid}'".format(wxid=wxid)
            self.c.execute(sql_command)
            new_points = self.c.fetchall()[0][0] + num
            sql_command = "UPDATE USERPOINTS SET POINTS={point} WHERE WXID='{wxid}'".format(point=new_points,
                                                                                            wxid=wxid)
            self.c.execute(sql_command)
            self.database.commit()
        finally:
            lock.release()  # 给线程解锁

    def minus_points(self, wxid, num):
        try:
            lock.acquire(True)  # 给线程上锁

            self._check_user(wxid)  # 检查是否存在
            self.add_points(wxid, num * -1)
        finally:
            lock.release()  # 给线程解锁

    def set_points(self, wxid, num):
        try:
            lock.acquire(True)  # 给线程上锁

            self._check_user(wxid)
            sql_command = "UPDATE USERPOINTS SET POINTS={point} WHERE WXID='{wxid}'".format(point=num,
                                                                                            wxid=wxid)
            self.c.execute(sql_command)
            self.database.commit()
        finally:
            lock.release()  # 给线程解锁

    def get_points(self, wxid):
        try:
            lock.acquire(True)  # 给线程上锁

            self._check_user(wxid)
            sql_command = "SELECT POINTS FROM USERPOINTS WHERE WXID='{wxid}'".format(wxid=wxid)
            self.c.execute(sql_command)
            result = self.c.fetchall()[0][0]
            return result
        finally:
            lock.release()  # 给线程解锁

    def get_stat(self, wxid):
        try:
            lock.acquire(True)  # 给线程上锁

            self._check_user(wxid)
            sql_command = "SELECT SIGNINSTAT FROM USERPOINTS WHERE WXID='{wxid}'".format(wxid=wxid)
            self.c.execute(sql_command)
            result = self.c.fetchall()[0][0]
            return result
        finally:
            lock.release()  # 给线程解锁

    def set_stat(self, wxid, num):
        try:
            lock.acquire(True)  # 给线程上锁

            self._check_user(wxid)
            sql_command = "UPDATE USERPOINTS SET SIGNINSTAT={SIGNINSTAT} WHERE WXID='{wxid}'".format(SIGNINSTAT=num,
                                                                                                     wxid=wxid)
            self.c.execute(sql_command)
            self.database.commit()  # 提交数据库
        finally:
            lock.release()  # 给线程解锁

    def reset_stat(self):
        try:
            lock.acquire(True)  # 给线程上锁

            sql_command = "UPDATE USERPOINTS SET SIGNINSTAT=0"
            self.c.execute(sql_command)
            self.database.commit()  # 提交数据库
        finally:
            lock.release()  # 给线程解锁

    def get_highest_points(self, num):
        try:
            lock.acquire(True)  # 给线程上锁

            sql_command = 'select * from USERPOINTS order by POINTS DESC, SIGNINSTAT LIMIT 0,{limit}'.format(limit=num)
            self.c.execute(sql_command)
            result = self.c.fetchall()
            return result
        finally:
            lock.release()  # 给线程解锁

    def set_whitelist(self, wxid, stat):
        try:
            lock.acquire(True)  # 给线程上锁

            self._check_user(wxid)
            sql_command = "UPDATE USERPOINTS SET WHITELIST={whitelist} WHERE WXID='{wxid}'".format(whitelist=stat,
                                                                                                   wxid=wxid)
            self.c.execute(sql_command)
            self.database.commit()  # 提交数据库
        finally:
            lock.release()

    def get_whitelist(self, wxid):
        try:
            lock.acquire(True)  # 给线程上锁

            self._check_user(wxid)
            sql_command = "SELECT WHITELIST FROM USERPOINTS WHERE WXID='{wxid}'".format(wxid=wxid)
            self.c.execute(sql_command)
            result = self.c.fetchall()[0][0]
            return result
        finally:
            lock.release()  # 给线程解锁
