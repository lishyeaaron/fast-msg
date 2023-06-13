# -*- coding: utf-8 -*-
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64


class EmailSender(object):
    def __init__(self, username, passwd, recv, title, content, file=None, email_host='smtp.163.com', port=25):
        """
        :param username: 用户名
        :param passwd: 密码 此处开启了smtp之后的密码是授权码
        :param recv: 收件人，多个要传list ['a@qq.com','b@qq.com]
        :param title: 邮件标题
        :param content: 邮件正文
        :param file: 附件路径，如果不在当前目录下，要写绝对路径，默认没有附件
        :param email_host: smtp服务器地址，默认为163服务器
        :param port: 链接端口，默认为25
        """
        self.username = username  # 用户名
        self.passwd = passwd  # 密码
        self.recv = recv  # 收件人，多个要传list ['a@qq.com','b@qq.com]
        self.title = title  # 邮件标题
        self.content = content  # 邮件正文
        self.file = file  # 附件路径，如果不在当前目录下，要写绝对路径
        self.email_host = email_host  # smtp服务器地址
        self.port = port  # 普通端口

    def send_mail(self):
        print('开始发送邮件')
        print(f'收件人：{self.recv}, 标题：{self.title}, 正文：{self.content}, 附件：{self.file}, '
              f'邮箱服务器：{self.email_host}, 端口：{self.port}, 用户名：{self.username}, 密码：{self.passwd}')
        msg = MIMEMultipart()
        # 发送内容的对象
        if self.file:  # 处理附件的
            file_name = os.path.split(self.file)[-1]  # 只取文件名，不取路径
            try:
                f = open(self.file, 'rb').read().split()
            except Exception:
                raise Exception('附件打不开！！！！')
            else:
                att = MIMEText(f, "base64", "utf-8")
                att["Content-Type"] = 'application/octet-stream'
                # base64.b64encode(file_name.encode()).decode()
                new_file_name = '=?utf-8?b?' + base64.b64encode(file_name.encode()).decode() + '?='
                # 这里是处理文件名为中文名的，必须这么写
                att["Content-Disposition"] = f'attachment; filename="{new_file_name}"'
                msg.attach(att)
        msg.attach(MIMEText(self.content))  # 邮件正文的内容
        msg['Subject'] = self.title  # 邮件主题
        msg['From'] = self.username  # 发送者账号
        print(self.recv)
        msg['To'] = ','.join(self.recv)  # 接收者账号列表
        # msg['Cc'] = ','.join(self.recv)  # 抄送者账号列表
        smtp = smtplib.SMTP_SSL(self.email_host, port=self.port)
        # 发送邮件服务器的对象
        smtp.login(self.username, self.passwd)
        try:

            smtp.sendmail(self.username, self.recv, msg.as_string())
        except Exception as e:
            r = False, str(e)
        else:
            r = True, '发送成功'
        print('发送结果：')
        print(r)
        smtp.quit()
        return r
