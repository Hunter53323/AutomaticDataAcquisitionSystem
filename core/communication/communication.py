from .drivers.driver_base import DriverBase
from .exception_handling import BreakdownHanding
import logging
from logging.handlers import RotatingFileHandler


class Communication:
    def __init__(self) -> None:
        self.drivers: list[DriverBase] = []
        self.__para_map: dict[str, DriverBase] = {}
        self.__data_map: dict[str, DriverBase] = {}
        self.__command_map: dict[str, DriverBase] = {}
        self.__is_read_all = False
        self.breakdown_handler = BreakdownHanding()
        self.logger = self.set_logger()

    def set_logger(self) -> logging.Logger:
        # 创建一个日志记录器
        logger = logging.getLogger("communication")
        logger.setLevel(logging.DEBUG)  # 设置日志级别
        formatter = logging.Formatter("%(asctime)s-%(module)s-%(funcName)s-%(lineno)d-%(name)s-%(message)s")  # 其中name为getlogger指定的名字

        rHandler = RotatingFileHandler(filename="./log/" + "communication" + ".log", maxBytes=1024 * 1024, backupCount=1)
        rHandler.setLevel(logging.DEBUG)
        rHandler.setFormatter(formatter)

        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(formatter)

        logger.addHandler(rHandler)
        logger.addHandler(console)
        return logger

    def __update_map(self, driver: DriverBase):
        self.__para_map.update({key: driver for key in driver.curr_para.keys()})
        self.__data_map.update({key: driver for key in driver.curr_data.keys()})
        self.__command_map.update({driver.command: driver})

    def write(self, para_dict: dict[str, any]) -> bool:
        para_command_map = {**self.__para_map, **self.__command_map}
        for driver in self.drivers:
            if driver.breakdown == True:
                self.logger.error(f"{driver.device_name}发生故障，请先处理故障")
                return False
        tmp_dict: dict[DriverBase, dict[str, any]] = {}
        error_key_list: list[str] = []
        for key, val in para_dict.items():
            if key not in para_command_map.keys():
                error_key_list.append(key)
                continue
            if para_command_map[key] not in tmp_dict.keys():
                tmp_dict[para_command_map[key]] = {}
            tmp_dict[para_command_map[key]].update({key: val})
        if error_key_list:
            self.logger.error(f"非法参数{error_key_list}")
            return False
        flag = True
        for key, val in tmp_dict.items():
            flag = flag & key.write(val)
        self.clear_curr_data()
        return flag

    def read(self, data_name_list: list[str] = None) -> dict[str, any]:
        result: dict[str, any] = {}
        if not data_name_list:
            for driver in self.drivers:
                result = {**result, **driver.read()}
            return result
        error_key_list: list[str] = []
        tmp_dict: dict[DriverBase, list[str]] = {}
        for key in data_name_list:
            if key not in self.__data_map.keys():
                error_key_list.append(key)
                continue
            if self.__data_map[key] not in tmp_dict.keys():
                tmp_dict[self.__data_map[key]] = []
            tmp_dict[self.__data_map[key]].append(key)
        if error_key_list:
            self.logger.error(f"非法参数{error_key_list}")
        for key, val in tmp_dict.items():
            result = {**result, **key.read(val)}
        return result

    def get_curr_para(self, para_name_list: list[str] = None) -> dict[str, any]:
        result: dict[str, any] = {}
        if not para_name_list:
            for driver in self.drivers:
                result = {**result, **driver.get_curr_para()}
            return result
        error_key_list: list[str] = []
        tmp_dict: dict[DriverBase, list[str]] = {}
        for key in para_name_list:
            if key not in self.__para_map.keys():
                error_key_list.append(key)
                continue
            if self.__para_map[key] not in tmp_dict.keys():
                tmp_dict[self.__para_map[key]] = []
            tmp_dict[self.__para_map[key]].append(key)
        if error_key_list:
            self.logger.error(f"非法参数{error_key_list}")
        for key, val in tmp_dict.items():
            result = {**result, **key.get_curr_para(val)}
        return result

    def register_device(self, driver: DriverBase) -> bool:
        self.drivers.append(driver)
        self.__update_map(driver)
        self.breakdown_handler.add_driver(driver)

    def find_driver(self, device_name: str) -> DriverBase:
        for driver in self.drivers:
            if driver.device_name == device_name:
                return driver
        return None

    def connect(self) -> bool:
        flag = True
        for driver in self.drivers:
            flag = flag & driver.connect()
        return flag

    def disconnect(self) -> bool:
        flag = True
        for driver in self.drivers:
            flag = flag & driver.disconnect()
        return flag

    def start_read_all(self) -> bool:
        flag = True
        for driver in self.drivers:
            flag = flag & driver.start_read_all()
        self.__is_read_all = True if flag else False
        return flag

    def get_para_map(self) -> dict[str, DriverBase]:
        return self.__para_map

    def get_data_map(self) -> dict[str, DriverBase]:
        return self.__data_map

    def get_device_and_para(self) -> dict[str, list]:
        device_para = {}
        for driver in self.drivers:
            device_para[driver.device_name] = list(driver.curr_para.keys())
        return device_para

    def stop_read_all(self) -> bool:
        flag = True
        for driver in self.drivers:
            flag = flag & driver.stop_read_all()
        self.__is_read_all = False if flag else True
        return flag

    def is_read_all(self) -> bool:
        return self.__is_read_all

    def check_thread_alive(self) -> bool:
        flag = True
        for driver in self.drivers:
            flag = flag & driver.check_thread_alive()
        return flag

    def update_hardware_parameter(self, device_name: str, para_dict: dict[str, any]) -> bool:
        err_key = []
        for driver in self.drivers:
            if driver.device_name == device_name:
                for key in para_dict.keys():
                    if key not in driver.hardware_para:
                        err_key.append(key)
                        self.logger.error(f"非法参数{key}")
                for key in err_key:
                    para_dict.pop(key)
                return driver.update_hardware_parameter(para_dict)
        return False

    def get_hardware_parameter(self, device_name: str) -> dict[str, any]:
        for driver in self.drivers:
            if driver.device_name == device_name:
                return driver.get_hardware_parameter()
        return {}

    def clear_curr_data(self):
        for driver in self.drivers:
            driver.clear_curr_data()
        return True
