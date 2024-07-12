from .drivers.fan_drive_module import FanDriver
from .drivers.actual_test_driver import TestDevice

BREAKDOWNMAP = {
    0: "采样偏置故障",
    1: "缺相故障",
    2: "硬件过流故障",
    3: "电机堵转故障",
    4: "电机失步故障",
    5: "软件 RMS 过流故障",
    6: "软件峰值过流故障",
    7: "直流母线欠压故障",
    8: "IPM 过温故障",
    9: "启动失败故障",
    10: "直流母线过压故障",
    11: "网压瞬时掉电故障",
}


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

    def judge_breakdown(self, breakdowns: list[int]) -> tuple[int, str]:
        # 判断故障类型，1是过流故障，2是普通故障

        for i in range(len(breakdowns)):
            if breakdowns[i] == 2 or breakdowns[i] == 5 or breakdowns[i] == 6:
                self.breakdown_type = 1
                return 1, BREAKDOWNMAP[breakdowns[i]]
        for i in range(len(breakdowns)):
            if 0 <= breakdowns[i] < 12:
                self.breakdown_type = 2
                return 2, BREAKDOWNMAP[breakdowns[i]]
        # 传错了，没故障
        self.breakdown_type = 0
        return 0, ""

    def handle_breakdown(self) -> bool:
        if self.breakdown_type == 0:
            # 无故障
            return True
        if self.breakdown_type == 1:
            # 过流故障，测试设备空载
            status = self.test_device.handle_breakdown(1)
            if not status:
                # 测试设备空载失败,可加日志
                return False
        # 风机驱动清障
        status = self.fan_driver.handle_breakdown(self.breakdown_type)
        if not status:
            # 风机空载失败,可加日志
            return False
        self.breakdown_type = 0
        return True

    def error_handle(self, breakdown: list[int]) -> tuple[bool, int, str]:
        """
        :retuen status: True是故障处理成功，False是故障处理失败
        :return breakdown_type: 1是过流故障，2是普通故障
        """
        breakdown_type, error = self.judge_breakdown(breakdown)
        return self.handle_breakdown(), breakdown_type, error

    def breakdown_warning(self):
        # 故障预警，发送提示信息
        pass
