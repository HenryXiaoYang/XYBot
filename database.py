import os
import sqlite3


class BotDatabase:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        super().__init__()

        if not os.path.exists('userpoints.db'):  # 检查数据库是否存在
            conn = sqlite3.connect('userpoints.db')
            c = conn.cursor()
            c.execute('CREATE TABLE USERPOINTS (WXID TEXT PRIMARY KEY, POINTS INT, SIGNINSTAT INT, WHITELIST INT)')
            conn.commit()
            c.close()
            conn.close()
        else:
            conn = sqlite3.connect('userpoints.db')
            conn.commit()
            conn.close()

        self.database = sqlite3.connect('userpoints.db')  # 连接数据库
        self.c = self.database.cursor()
        self.c.execute('select u.WXID from USERPOINTS u;')  # 获取已有用户列表
        self.wxid_list = self.c.fetchall()

    def _check_user(self, wxid):
        if not (wxid,) in self.wxid_list:  # 不存在，创建用户并设置积分为增加的积分
            sql_command = "INSERT INTO USERPOINTS VALUES {}".format((wxid, 0, 0, 0))
            self.c.execute(sql_command)
            self.database.commit()  # 提交数据库

    def add_points(self, wxid, num):
        self._check_user(wxid)
        sql_command = "SELECT POINTS FROM USERPOINTS WHERE WXID='{wxid}'".format(wxid=wxid)
        self.c.execute(sql_command)
        new_points = self.c.fetchall()[0][0] + num
        sql_command = "UPDATE USERPOINTS SET POINTS={point} WHERE WXID='{wxid}'".format(point=new_points,
                                                                                        wxid=wxid)
        self.c.execute(sql_command)
        self.database.commit()

    def minus_points(self, wxid, num):  # 检查是否存在
        self.add_points(wxid, num * -1)

    def set_points(self, wxid, num):
        self._check_user(wxid)
        sql_command = "UPDATE USERPOINTS SET POINTS={point} WHERE WXID='{wxid}'".format(point=num,
                                                                                        wxid=wxid)
        self.c.execute(sql_command)
        self.database.commit()

    def get_points(self, wxid):
        self._check_user(wxid)
        sql_command = "SELECT POINTS FROM USERPOINTS WHERE WXID='{wxid}'".format(wxid=wxid)
        self.c.execute(sql_command)
        result = self.c.fetchall()[0][0]
        return result

    def get_stat(self, wxid):
        self._check_user(wxid)
        sql_command = "SELECT SIGNINSTAT FROM USERPOINTS WHERE WXID='{wxid}'".format(wxid=wxid)
        self.c.execute(sql_command)
        result = self.c.fetchall()[0][0]
        return result

    def set_stat(self, wxid, num):
        self._check_user(wxid)
        sql_command = "UPDATE USERPOINTS SET SIGNINSTAT={SIGNINSTAT} WHERE WXID='{wxid}'".format(SIGNINSTAT=num,
                                                                                                 wxid=wxid)
        self.c.execute(sql_command)
        self.database.commit()  # 提交数据库

    def reset_stat(self):
        sql_command = "UPDATE USERPOINTS SET SIGNINSTAT=0"
        self.c.execute(sql_command)
        self.database.commit()  # 提交数据库

    def get_highest_points(self, num):
        sql_command = 'select * from USERPOINTS order by POINTS DESC, SIGNINSTAT LIMIT 0,{limit}'.format(limit=num)
        self.c.execute(sql_command)
        result = self.c.fetchall()
        return result

    def set_whitelist(self, wxid, stat):
        self._check_user(wxid)
        sql_command = "UPDATE USERPOINTS SET WHITELIST={whitelist} WHERE WXID='{wxid}'".format(whitelist=stat,
                                                                                               wxid=wxid)
        self.c.execute(sql_command)
        self.database.commit()  # 提交数据库

    def get_whitelist(self, wxid):
        self._check_user(wxid)
        sql_command = "SELECT WHITELIST FROM USERPOINTS WHERE WXID='{wxid}'".format(wxid=wxid)
        self.c.execute(sql_command)
        result = self.c.fetchall()[0][0]
        return result
