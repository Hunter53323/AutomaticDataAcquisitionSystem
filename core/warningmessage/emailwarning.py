import smtplib
from email.mime.text import MIMEText
from email.header import Header

from core.utils import save_json, read_json
import json

import requests


class EmailWarning:
    def __init__(self) -> None:
        self.sender_mail: str = "sjzdcjxt@126.com"
        self.sender_passwd: str = "ZUJVWGWLPKZGVSCQ"
        self.receiver_email: str = read_json("receiver_email")
        self.receiver_name: str = read_json("receiver_name")

    def set_sender_mail(self, sender_mail: str, sender_passwd: str) -> None:
        self.sender_mail = sender_mail
        self.sender_passwd = sender_passwd
        save_json({"sender_mail": sender_mail, "sender_passwd": sender_passwd})

    def set_receiver(self, receiver_name: str, receiver_email: str) -> bool:
        data_dict: dict = read_json("data_dict")
        send_flag = True
        if not data_dict:
            data_dict = {}
        if not receiver_email:
            if receiver_name in data_dict.keys():
                receiver_email = data_dict[receiver_name]
                send_flag = False
            else:
                return False
        self.receiver_name = receiver_name
        self.receiver_email = receiver_email
        data_dict.update({receiver_name: receiver_email})
        save_json({"receiver_email": receiver_email, "receiver_name": receiver_name, "data_dict": data_dict})
        if send_flag:
            return self.send_test_email()
        else:
            return True

    def get_smtp_server(self, email: str) -> tuple[str, int]:
        """
        根据邮箱域名获取SMTP服务器地址和端口。
        """
        if "qq.com" in email:
            return "smtp.qq.com", 465
        elif "163.com" in email:
            return "smtp.163.com", 465
        elif "126.com" in email:
            return "smtp.126.com", 465
        else:
            raise ValueError("不支持的邮箱类型")

    def send_test_email(self) -> bool:
        """
        发送测试邮件的函数。
        """
        return self.send_email("测试邮件", "这是一封测试邮件")

    def send_email(self, subject: str, message: str) -> bool:
        """
        发送邮件的函数。

        :param subject: 邮件主题
        :param message: 邮件正文内容
        """
        if not self.check():
            return False
        # 创建一个MIMEText邮件对象，设置邮件内容和格式
        msg = MIMEText(message, "plain", "utf-8")
        msg["From"] = Header(self.sender_mail)
        msg["To"] = Header(self.receiver_email)
        msg["Subject"] = Header(subject)

        # 根据接收者的邮箱域名获取SMTP服务器和端口
        smtp_server, port = self.get_smtp_server(self.sender_mail)

        # 连接到SMTP服务器并发送邮件
        try:
            server = smtplib.SMTP_SSL(smtp_server, port)
            server.login(self.sender_mail, self.sender_passwd)  # 登录验证
            server.sendmail(self.sender_mail, [self.receiver_email], msg.as_string())  # 发送邮件
            send_feishu(subject + ":" + message)
            return True
        except smtplib.SMTPException as e:
            print(e)
            return False
        finally:
            server.quit()

    def check(self) -> bool:
        if self.sender_mail and self.sender_passwd and self.receiver_email and self.receiver_name:
            return True
        return False


def send_feishu(message: str):

    # 飞书Webhook的URL
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/2cbc51eb-7c28-44df-946c-06b0f38770be"

    # 要发送的消息内容
    message = {"msg_type": "text", "content": {"text": message}}

    # 将消息内容转换为JSON格式
    headers = {"Content-Type": "application/json"}
    data = json.dumps(message)

    # 发送POST请求到Webhook
    response = requests.post(webhook_url, headers=headers, data=data)


if __name__ == "__main__":
    send_feishu("测试")
