import smtplib
from email.mime.text import MIMEText
from email.header import Header
from core.utils import save_json, read_json


class EmailWarning:
    def __init__(self) -> None:
        self.sender_mail: str = read_json("sender_mail")
        self.sender_passwd: str = read_json("sender_passwd")
        self.receiver_email: str = read_json("receiver_email")
        self.receiver_name: str = read_json("receiver_name")

    def set_sender_mail(self, sender_mail: str, sender_passwd: str) -> None:
        self.sender_mail = sender_mail
        self.sender_passwd = sender_passwd
        save_json({"sender_mail": sender_mail, "sender_passwd": sender_passwd})

    def set_receiver(self, receiver_name: str, receiver_email: str) -> None:
        self.receiver_name = receiver_name
        self.receiver_email = receiver_email
        save_json({"receiver_email": receiver_email, "receiver_name": receiver_name})
        self.send_test_email()

    def get_smtp_server(self, email: str) -> tuple[str, int]:
        """
        根据邮箱域名获取SMTP服务器地址和端口。
        """
        if "qq.com" in email:
            return "smtp.qq.com", 465
        elif "126.com" in email or "163.com" in email:
            return "smtp.163.com", 465
        else:
            raise ValueError("不支持的邮箱类型")

    def send_test_email(self) -> bool:
        """
        发送测试邮件的函数。
        """
        return self.send_email("测试邮件", self.receiver, "这是一封测试邮件")

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
        smtp_server, port = self.get_smtp_server(self.receiver_email)

        # 连接到SMTP服务器并发送邮件
        try:
            server = smtplib.SMTP_SSL(smtp_server, port)
            server.login(self.sender_mail, self.sender_passwd)  # 登录验证
            server.sendmail(self.sender_mail, [self.receiver_email], msg.as_string())  # 发送邮件
            return True
        except smtplib.SMTPException as e:
            return False
        finally:
            server.quit()

    def check(self) -> bool:
        if self.sender_mail and self.sender_passwd and self.receiver_email and self.receiver_name:
            return True
        return False
