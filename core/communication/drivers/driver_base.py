from abc import ABC, abstractmethod
from threading import Thread, Event
import logging
from logging.handlers import RotatingFileHandler
import time


class DriverBase(ABC):
    def __init__(self, device_name: str):
        self.device_name = device_name
        self.conn_state = False
        self.run_state = False
        self.breakdown = False
        self.__read_all_running: bool = False
        self.__iswriting = False
        self.__isreading = False
        self.read_error = False
        self.write_error = False
        # self.curr_data = {key: 0 for key in data_list}
        # self.curr_para = {key: 0 for key in para_list}
        self.curr_data = {}
        self.curr_para = {}
        self.command = None
        self.hardware_para = []
        self.logger = self.set_logger()
        pass

    def set_logger(self):
        # 创建一个日志记录器
        logger = logging.getLogger(self.device_name)
        logger.setLevel(logging.DEBUG)  # 设置日志级别
        formatter = logging.Formatter("%(asctime)s-%(module)s-%(funcName)s-%(lineno)d-%(name)s-%(message)s")  # 其中name为getlogger指定的名字

        rHandler = RotatingFileHandler(filename="./log/" + self.device_name + ".log", backupCount=1)
        rHandler.setLevel(logging.DEBUG)
        rHandler.setFormatter(formatter)

        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(formatter)

        logger.addHandler(rHandler)
        logger.addHandler(console)
        return logger

    @abstractmethod
    def connect(self) -> bool:
        return True

    @abstractmethod
    def disconnect(self) -> bool:
        return True

    @abstractmethod
    def write_execute(self) -> bool:
        pass

    @abstractmethod
    def read_all(self) -> bool:
        pass

    @abstractmethod
    def handle_breakdown(self, breakdowns: list[int]) -> bool:
        pass

    @abstractmethod
    def update_hardware_parameter(self, para_dict: dict[str, any]) -> bool:
        pass

    @abstractmethod
    def get_hardware_parameter(self) -> dict[str, any]:
        pass

    @abstractmethod
    def export_config(self) -> dict[str, str]:
        # 导出设备的所有配置为一个字典，value只能为int,float,str,bool
        pass

    @abstractmethod
    def load_config(self, config: dict[str, str]) -> bool:
        # 从一个字典中加载配置
        pass

    @abstractmethod
    def get_database_table(self) -> dict[str, str]:
        # 获取要存储到数据库中的所有数据名及类型
        pass

    @abstractmethod
    def close_device(self) -> bool:
        # 关闭设备
        pass

    def get_device_state(self) -> dict[str, any]:
        # 当前是否连接，设备当前是否启动，设备当前是否故障
        return {"连接状态": self.conn_state, "运行状态": self.run_state, "故障": self.breakdown}

    def is_connected(self) -> bool:
        return self.conn_state

    def is_read_all_running(self) -> bool:
        return self.__read_all_running

    def read(self, data_name_list: list[str] = None) -> dict[str, any]:
        if not self.__read_all_running:
            # print(f"{self.device_name}read_all线程尚未启动")
            self.logger.debug(f"{self.device_name}read_all线程尚未启动")
            return {}
        if not data_name_list:
            return self.curr_data
        result = {}
        for key in data_name_list:
            result = {**result, key: self.curr_data[key]}
        return result

    def start_read_all(self) -> bool:
        if self.__read_all_running:
            print(f"{self.device_name}:read_all线程无需重复启动")
            return False
        self.__stop_event = Event()
        self.__read_Thread = Thread(target=self.__read_all_loop, args=(self.__stop_event,))
        self.__read_Thread.start()
        self.__read_all_running = True
        print(f"{self.device_name}:read_all线程已启动")
        return True

    def stop_read_all(self) -> bool:
        if not self.__read_all_running:
            print(f"{self.device_name}:read_all线程未启动")
            return True
        self.__stop_event.set()
        self.__read_Thread.join()
        print("read_all线程已停止")
        self.__read_all_running = False
        return True

    def __read_all_loop(self, stop_event: Event):
        while True:
            if stop_event.is_set():
                print(f"{self.device_name}:read_all线程正在退出")
                break
            count = 0
            while self.__iswriting:
                count += 1
                time.sleep(0.005)
                if count == 1000:
                    self.logger.error(f"串口不可读!")
                    self.read_error = True
                    break
            self.__isreading = True
            if not self.read_all():
                self.read_error = True
                self.logger.error(f"{self.device_name}读取数据失败")
                break
            self.__isreading = False
            time.sleep(0.05)

    def write(self, para_dict: dict[str, any]) -> bool:
        if not self.check_writable():
            self.logger.error(f"串口不可写!")
            self.write_error = True
            return False
        self.__iswriting = True
        status = self.write_execute(para_dict)
        self.write_error = not status
        self.__iswriting = False
        return status

    def check_thread_alive(self) -> bool:
        if not self.__read_Thread.is_alive():
            self.start_read_all()
            if not self.__read_Thread.is_alive():
                return False
        return True

    def check_writable(self) -> bool:
        count = 0
        while self.__isreading:
            time.sleep(0.005)
            count += 1
            if count == 1000:
                # 若5秒都没有读取成功，那么报错
                self.logger.error(f"串口不可写!")
                return False
        return True

    def get_curr_para(self, para_name_list: list[str] = None) -> dict[str, any]:
        if not para_name_list:
            return self.curr_para
        result = {}
        for key in para_name_list:
            result = {**result, key: self.curr_para[key]}
        return result

    def clear_curr_data(self):
        self.curr_data = {key: 0 for key in self.curr_data.keys()}

    def check_error(self):
        return self.read_error or self.write_error

    def reset_status(self):
        if self.__read_all_running:
            self.stop_read_all()
            self.__read_all_running: bool = False
        self.conn_state = False
        self.run_state = False
        self.breakdown = False
        self.__iswriting = False
        self.__isreading = False
        self.read_error = False
        self.write_error = False
