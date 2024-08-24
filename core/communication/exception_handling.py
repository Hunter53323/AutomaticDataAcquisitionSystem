from .drivers.fan_drive_module import FanDriver
from .drivers.actual_test_driver import TestDevice
from core.warningmessage import emailsender


class BreakdownHanding:
    def __init__(self):
        self.test_device = None
        self.fan_driver = None
        self.breakdown_type = 0

    def add_driver(self, driver: TestDevice | FanDriver) -> None:
        if driver.device_name == "FanDriver":
            self.fan_driver = driver
        elif driver.device_name == "TestDevice":
            self.test_device = driver
        else:
            raise Exception("Invalid driver")

    def breakdown_handler_ready(self) -> bool:
        if self.test_device is None or self.fan_driver is None:
            return False
        return True

    def judge_breakdown(self, breakdowns: list[str]) -> tuple[int, str]:
        # 判断故障类型，1是过流故障，2是普通故障

        for i in range(len(breakdowns)):
            if "过流" in breakdowns[i]:
                self.breakdown_type = 1
                return 1, breakdowns[i]
            else:
                self.breakdown_type = 2
                return 2, breakdowns[i]
        # 传错了，没故障
        self.breakdown_type = 0
        return 0, ""

    def handle_breakdown(self) -> bool:
        breakdown_description = ["无故障", "过流故障", "普通故障"]
        if self.breakdown_type == 0:
            # 无故障
            return True
        if self.breakdown_type == 1:
            # 过流故障，测试设备空载
            pass
        status = self.test_device.handle_breakdown(1)
        if not status:
            # 测试设备空载失败,可加日志
            emailsender.send_email("数采系统故障通知", "发生过流故障，自动处理失败，请立即查看")
            return False
        # 风机驱动清障
        print("风机驱动清障")
        print(type(self.breakdown_type))
        print(self.breakdown_type)
        status = self.fan_driver.handle_breakdown(self.breakdown_type)
        if not status:
            # 风机空载失败,可加日志
            emailsender.send_email("数采系统故障通知", f"发生{breakdown_description[self.breakdown_type]}，风机空载失败，请立即查看")
            return False

        # emailsender.send_email("数采系统故障通知", f"发生{breakdown_description[self.breakdown_type]}，自动清障成功")
        self.breakdown_type = 0
        return True

    def error_handle(self, breakdown: list[str]) -> tuple[bool, int, str]:
        """
        :retuen status: True是故障处理成功，False是故障处理失败
        :return breakdown_type: 1是过流故障，2是普通故障
        """
        breakdown_type, error = self.judge_breakdown(breakdown)
        return self.handle_breakdown(), breakdown_type, error
