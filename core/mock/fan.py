import threading
import random
import time


class Fan:
    def __init__(self):
        # 查询数据
        self.target_speed = 0
        self.actual_speed = 0
        self.dc_bus_voltage = 0
        self.U_phase_current = 0
        self.power = 0
        self.breakdown = 0

        self.state = False
        self.control_time = time.time()
        self.stop_event = threading.Event()
        self.thread = None

    def fanstart(self):
        while not self.stop_event.is_set():
            speed_error = self.target_speed - self.actual_speed
            P = (1 + random.random()) * speed_error / 20
            self.actual_speed += P
            self.dc_bus_voltage = self.actual_speed * 5 + random.randint(0, 10)
            self.U_phase_current = self.actual_speed / 10 + random.randint(0, 10)
            self.power = self.actual_speed / 10 + random.randint(0, 10)
            time.sleep(0.05)
            # print("设定转速：", self.target_speed, "实际转速：", self.actual_speed)

    def thread_start(self):
        self.thread = threading.Thread(target=self.fanstart)
        self.thread.start()

    def control(self, state: bool, set_speed: int):
        self.state = state
        if self.state == False:
            self.target_speed = 0
        else:
            self.target_speed = set_speed * 21.83

    def read(self):
        return (
            round(self.target_speed),
            round(self.actual_speed),
            round(self.dc_bus_voltage),
            round(self.U_phase_current),
            round(self.power),
            self.breakdown,
        )

    def stop(self):
        self.stop_event.set()  # 设置事件，通知线程停止
        self.thread.join()  # 等待线程结束


if __name__ == "__main__":
    fan = Fan()
    fan.thread_start()
    try:
        while True:
            time.sleep(5)
            fan.control(True, 100)
            time.sleep(5)
            fan.control(False, 0)
            time.sleep(5)
            fan.control(True, 200)
            time.sleep(5)
            fan.control(True, 300)
            time.sleep(5)
    except KeyboardInterrupt:
        fan.stop()  # 在捕获到键盘中断时调用stop方法停止线程
