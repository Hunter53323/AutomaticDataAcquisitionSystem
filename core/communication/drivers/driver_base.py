from abc import ABC, abstractmethod
from threading import Thread, Event
import logging
from logging.handlers import RotatingFileHandler
import time


class DriverBase(ABC):
    def __init__(self, device_name: str, data_list: list[str], para_list: list[str]):
        self.device_name = device_name
        self.conn_state = False
        self.__read_all_running: bool = False
        self.curr_data = {key: None for key in data_list}
        self.curr_para = {key: None for key in para_list}
        self.hardware_para = []
        self.logger = self.set_logger()
        pass

    def set_logger(self):
        # 创建一个日志记录器
        logger = logging.getLogger(self.device_name)
        logger.setLevel(logging.ERROR)  # 设置日志级别
        formatter = logging.Formatter('%(asctime)s-%(module)s-%(funcName)s-%(lineno)d-%(name)s-%(message)s')# 其中name为getlogger指定的名字

        rHandler = RotatingFileHandler(filename="../../../log/"+self.device_name+".log", maxBytes=1024 * 1024, backupCount=1)
        rHandler.setLevel(logging.ERROR)
        rHandler.setFormatter(formatter)

        console = logging.StreamHandler()
        console.setLevel(logging.ERROR)
        console.setFormatter(formatter)

        logger.addHandler(rHandler)
        logger.addHandler(console)
        return logger

    @abstractmethod
    def write(self, para_dict: dict[str, any]) -> bool:
        pass

    @abstractmethod
    def connect(self) -> bool:
        return True
    
    @abstractmethod
    def disconnect(self) -> bool:
        return True
    
    @abstractmethod
    def read_all(self) -> bool:
        pass
    @abstractmethod
    def breakdown(self,breakdowns: list[int]) -> bool:
        pass

    @abstractmethod
    def update_hardware_parameter(self, para_dict: dict[str, any]) -> bool:
        pass

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
            print(f"{self.device_name}read_all线程已启动")
            return False
        self.__stop_event = Event()
        self.__read_Thread = Thread(target=self.__read_all_loop, args=(self.__stop_event,))
        self.__read_Thread.start()
        self.__read_all_running = True
        return True
    
    def stop_read_all(self) -> bool:
        if not self.__read_all_running:
            print(f"{self.device_name}read_all线程未启动")
            return True
        self.__stop_event.set()
        self.__read_Thread.join()
        print("read_all线程已停止")
        self.__read_all_running = False
        return True

    def __read_all_loop(self, stop_event: Event):
        while True:
            if stop_event.is_set():
                print(f"{self.device_name}read_all线程正在退出")
                break
            self.read_all()
            time.sleep(0.05)

    def get_curr_para(self, para_name_list: list[str] = None) -> dict[str, any]:
        if not para_name_list:
            return self.curr_para
        result = {}
        for key in para_name_list:
            result = {**result, key: self.curr_para[key]}
        return result