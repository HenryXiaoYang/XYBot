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
            c.execute('''CREATE TABLE USERPOINTS (WXID TEXT, POINTS INT, SIGNINSTAT INT, WHITELIST INT)''')
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

    def add_points(self, wxid, num):
        if not (wxid,) in self.wxid_list:  # 不存在，创建用户并设置积分为增加的积分
            sql_command = "INSERT INTO USERPOINTS VALUES {}".format((wxid, num, 0, 0))
            self.c.execute(sql_command)
            self.database.commit()  # 提交数据库
            return True

        else:  # 存在，获取旧积分值并更改为新积分值
            sql_command = "SELECT POINTS FROM USERPOINTS WHERE WXID='{wxid}'".format(wxid=wxid)
            self.c.execute(sql_command)
            new_points = self.c.fetchall()[0][0] + num
            sql_command = "UPDATE USERPOINTS SET POINTS={point} WHERE WXID='{wxid}'".format(point=new_points,
                                                                                            wxid=wxid)
            self.c.execute(sql_command)
            self.database.commit()
            return True

    def minus_points(self, wxid, num):  # 检查是否存在
        if not (wxid,) in self.wxid_list:  # 不存在，创建用户并把积分设置为（0-需减积分）
            sql_command = "INSERT INTO USERPOINTS VALUES '{}'".format((wxid, 0 - num, 0, 0))
            self.c.execute(sql_command)
            self.database.commit()  # 提交数据库
            return True

        else:  # 存在，获取旧积分值并更改为新积分值
            sql_command = "SELECT POINTS FROM USERPOINTS WHERE WXID='{wxid}'".format(wxid=wxid)
            self.c.execute(sql_command)
            new_points = self.c.fetchall()[0][0] - num
            sql_command = "UPDATE USERPOINTS SET POINTS={point} WHERE WXID='{wxid}'".format(point=new_points,
                                                                                            wxid=wxid)
            self.c.execute(sql_command)
            self.database.commit()  # 提交数据库
            return True

    def get_points(self, wxid):
        if not (wxid,) in self.wxid_list:  # 不存在，创建用户并设置积分为0
            sql_command = "INSERT INTO USERPOINTS VALUES '{}'".format((wxid, 0, 0, 0))
            self.c.execute(sql_command)
            sql_command = "SELECT POINTS FROM USERPOINTS WHERE WXID='{wxid}'".format(wxid=wxid)
            self.c.execute(sql_command)
            result = self.c.fetchall()[0][0]
            self.database.commit()  # 提交数据库
            return result

        else:  # 存在，查询并返回积分
            sql_command = "SELECT POINTS FROM USERPOINTS WHERE WXID='{wxid}'".format(wxid=wxid)
            self.c.execute(sql_command)
            result = self.c.fetchall()[0][0]
            return result

    def get_stat(self, wxid):
        if not (wxid,) in self.wxid_list:  # 不存在，创建用户并设置上次签到状态为0
            sql_command = "INSERT INTO USERPOINTS VALUES {}".format((wxid, 0, 0, 0))
            self.c.execute(sql_command)
            self.database.commit()
            sql_command = "SELECT SIGNINSTAT FROM USERPOINTS WHERE WXID='{wxid}'".format(wxid=wxid)
            self.c.execute(sql_command)
            result = self.c.fetchall()[0][0]
            return result

        else:  # 存在，查询并返回上次签到状态
            sql_command = "SELECT SIGNINSTAT FROM USERPOINTS WHERE WXID='{wxid}'".format(wxid=wxid)
            self.c.execute(sql_command)
            result = self.c.fetchall()[0][0]
            return result

    def set_stat(self, wxid, num):
        if not (wxid,) in self.wxid_list:  # 不存在，创建用户并设置上次签到状态为num
            sql_command = "INSERT INTO USERPOINTS VALUES '{}'".format((wxid, 0, num, 0))
            self.c.execute(sql_command)
            self.database.commit()  # 提交数据库
            return True

        else:  # 存在，获取旧时间并设置新状态
            sql_command = "SELECT SIGNINSTAT FROM USERPOINTS WHERE WXID='{wxid}'".format(wxid=wxid)
            self.c.execute(sql_command)
            sql_command = "UPDATE USERPOINTS SET SIGNINSTAT={SIGNINSTAT} WHERE WXID='{wxid}'".format(SIGNINSTAT=num,
                                                                                                     wxid=wxid)
            self.c.execute(sql_command)
            self.database.commit()  # 提交数据库
            return True

    def reset_stat(self):
        sql_command = "UPDATE USERPOINTS SET SIGNINSTAT=0"
        self.c.execute(sql_command)
        self.database.commit()  # 提交数据库
        return True

    def get_highest_points(self, num):
        sql_command = 'select * from USERPOINTS order by POINTS DESC, SIGNINSTAT LIMIT 0,{limit}'.format(limit=num)
        self.c.execute(sql_command)
        result = self.c.fetchall()
        return result

    def set_whitelist(self, wxid, stat):
        if not (wxid,) in self.wxid_list:
            if stat == '加入':
                num = 1
            elif stat == '删除':
                num = 0
            else:
                num = 0
            sql_command = "INSERT INTO USERPOINTS VALUES '{}'".format((wxid, 0, 0, num))
            self.c.execute(sql_command)
            self.database.commit()  # 提交数据库
            return True
        else:
            if stat == '加入':
                num = 1
            elif stat == '删除':
                num = 0
            else:
                num = 0
            sql_command = "UPDATE USERPOINTS SET WHITELIST={whitelist} WHERE WXID='{wxid}'".format(whitelist=num,
                                                                                                   wxid=wxid)
            self.c.execute(sql_command)
            self.database.commit()  # 提交数据库
            return True

    def get_whitelist(self, wxid):
        if not (wxid,) in self.wxid_list:
            sql_command = "INSERT INTO USERPOINTS VALUES '{}'".format((wxid, 0, 0, 0))
            self.c.execute(sql_command)
            self.database.commit()  # 提交数据库
            return 0
        else:
            sql_command = "SELECT WHITELIST FROM USERPOINTS WHERE WXID='{wxid}'".format(wxid=wxid)
            self.c.execute(sql_command)
            result = self.c.fetchall()[0][0]
            return result
