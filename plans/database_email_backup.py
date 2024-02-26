#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pywxdll
import schedule
import yaml
from loguru import logger

from plans_interface import PlansInterface


class database_email_backup(PlansInterface):
    def __init__(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        main_config_path = os.path.join(current_directory, '../main_config.yml')
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config['ip']
        self.port = main_config['port']
        self.timezone = main_config['timezone']
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

    def job(self):
        mail_host = "smtp.163.com"  # 设置服务器
        mail_user = "henryyang888@163.com"  # 用户名
        mail_pass = "MAMPSFVYXQCVDDYZ"  # 口令

        sender = 'henryyang888@163.com'
        receiver = 'henryyang888@163.com'

        mail_subject = f'XYBot数据库备份 {time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())}'
        mail_text = f"""
        <h1>XYBot数据库备份</h1>
        <p>时间：{time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())}</p>
        """
        mail_attach_file_path = 'userpoints.db'

        email = MIMEMultipart()
        email['From'] = sender
        email['To'] = receiver
        email['Subject'] = mail_subject
        email.attach(MIMEText(mail_text, 'html', 'utf-8'))

        attachment = MIMEText(open(mail_attach_file_path, 'rb').read(), 'base64', 'utf-8')  # 添加附件
        attachment["Content-Type"] = 'application/octet-stream'  # 设置类型
        attachment["Content-Disposition"] = f'attachment; filename="{mail_attach_file_path}"'  # 设置邮件用现实的名称
        email.attach(attachment)

        try:
            mailServer = smtplib.SMTP(mail_host, 25)  # 25为端口号(邮件）
            mailServer.login(mail_user, mail_pass)  # 需要的是，邮箱的地址和授权密码
            mailServer.sendmail(mail_user, receiver, email.as_string())
            mailServer.close()  # 关闭连接
            logger.success('数据库邮件发送成功！')
        except Exception as e:
            logger.error(e)

    def run(self):
        schedule.every().day.at('06:00').do(self.job)
