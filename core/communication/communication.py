from .drivers.driver_base import DriverBase
from .exception_handling import BreakdownHanding
import logging
from logging.handlers import RotatingFileHandler
import re


class Communication:
    def __init__(self) -> None:
        self.drivers: list[DriverBase] = []
        self.__para_map: dict[str, DriverBase] = {}
        self.__data_map: dict[str, DriverBase] = {}
        self.custom_calculate_map: dict[str, str] = {}
        self.__command_map: dict[str, DriverBase] = {}
        self.__is_read_all: list = []
        self.breakdown_handler = BreakdownHanding()
        self.logger = self.set_logger()
        self.conn_state: list = []
        # TODO:这里考虑自定义的运算如何和参数表和数据表进行匹配，不然好像会出问题

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

    def update_map(self, driver: DriverBase):
        # 更新设备匹配的所有数据参数表
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
        # self.clear_curr_data()
        return flag

    def read(self) -> dict[str, any]:
        result: dict[str, any] = {}
        for driver_name in self.__is_read_all:
            driver = self.find_driver(driver_name)
            result = {**result, **driver.read()}
        return result

    def get_curr_para(self) -> dict[str, any]:
        result: dict[str, any] = {}
        for driver_name in self.__is_read_all:
            driver = self.find_driver(driver_name)
            result = {**result, **driver.get_curr_para()}
        return result

    def register_device(self, driver: DriverBase) -> bool:
        self.drivers.append(driver)
        self.update_map(driver)
        self.breakdown_handler.add_driver(driver)

    def find_driver(self, device_name: str) -> DriverBase:
        for driver in self.drivers:
            if driver.device_name == device_name:
                return driver
        return None

    def connect(self, device_name: str = "") -> bool:
        if not device_name:
            flag = True
            for driver in self.drivers:
                flag = flag & driver.connect()
            self.conn_state = [driver.device_name for driver in self.drivers]
            return flag
        if device_name in self.conn_state:
            return True
        for driver in self.drivers:
            if driver.device_name == device_name:
                flag = driver.connect()
                break
        if flag:
            self.conn_state.append(device_name)
            return True
        return False

    def disconnect(self, device_name: str = "") -> bool:
        if not device_name:
            flag = True
            for driver in self.drivers:
                flag = flag & driver.disconnect()
            self.conn_state = []
            return flag
        if device_name not in self.conn_state:
            return False
        for driver in self.drivers:
            if driver.device_name == device_name:
                flag = driver.disconnect()
                break
        if flag:
            self.conn_state.remove(device_name)
            return True
        return False

    def is_connected(self, device_name: str = "") -> bool:
        if not device_name:
            return len(self.conn_state) == len(self.drivers)
        if device_name in self.conn_state:
            return True
        return False

    def start_read_all(self, device_name: str = "") -> bool:
        if not device_name:
            flag = True
            for driver in self.drivers:
                flag = flag & driver.start_read_all()
            self.__is_read_all = [driver.device_name for driver in self.drivers]
            return flag
        for driver in self.drivers:
            if driver.device_name == device_name:
                flag = driver.start_read_all()
                break
        if flag:
            self.__is_read_all.append(device_name)
            return True
        return False

    def stop_read_all(self, device_name: str = "") -> bool:
        if not device_name:
            flag = True
            for driver in self.drivers:
                flag = flag & driver.stop_read_all()
            self.__is_read_all = []
            return flag
        for driver in self.drivers:
            if driver.device_name == device_name:
                flag = driver.stop_read_all()
                break
        if flag:
            self.__is_read_all.remove(device_name)
            return True
        return False

    def is_read_all(self, device_name: str = "") -> bool:
        # 判断是否所有设备都在读取数据，或者判断某个设备是否在读取数据,返回值为是否在读取数据以及当前正在读取的设备数量
        if not device_name:
            return len(self.__is_read_all) == len(self.drivers)
        if device_name in self.__is_read_all:
            return True
        return False

    def read_all_driver_number(self) -> int:
        return len(self.__is_read_all)

    def check_thread_alive(self, device_name: str = "") -> bool:
        if not device_name:
            flag = True
            for driver in self.drivers:
                flag = flag & driver.check_thread_alive()
            return flag
        for driver in self.drivers:
            if driver.device_name == device_name:
                return driver.check_thread_alive()
        return False

    def get_para_map(self) -> dict[str, DriverBase]:
        return self.__para_map

    def get_data_map(self) -> dict[str, DriverBase]:
        return self.__data_map

    def get_device_and_para(self) -> dict[str, list]:
        device_para = {}
        for driver in self.drivers:
            device_para[driver.device_name] = list(driver.curr_para.keys())
        return device_para

    def get_device_and_data(self) -> dict[str, list]:
        device_data = {}
        for driver in self.drivers:
            device_data[driver.device_name] = list(driver.curr_data.keys())
        return device_data

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

    def get_device_state(self) -> dict[str, any]:
        state_dict = {}
        for driver in self.drivers:
            state_dict[driver.device_name] = driver.get_device_state()
        return state_dict

    def clear_curr_data(self):
        for driver in self.drivers:
            driver.clear_curr_data()
        return True

    def get_cureent_data_table(self) -> dict[str, any]:
        # 根据已有的数据构造数据表，进一步构造新的数据库表
        # TODO:根据用户配置的自定义运算逻辑添加到数据库表中
        table_columns = {"ID": "INT AUTO_INCREMENT PRIMARY KEY"}
        for driver in self.drivers:
            tmp_table = driver.get_database_table()
            for key, value in tmp_table.items():
                if key not in table_columns.keys():
                    table_columns[key] = type2sqltype(value)
                else:
                    raise ValueError(f"数据表中存在重复的列名{key}")
        table_columns.update(self.get_custom_column())
        table_columns.update({"时间戳": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"})

        return table_columns

    ##################################用户自定义的运算逻辑##################################

    def get_custom_column(self) -> dict[str, any]:
        # 获取用户自定义的运算的列名,用于构造数据库表
        return {key: "FLOAT" for key in self.custom_calculate_map.keys()}

    def add_custom_column(self, user_input: list[str]) -> bool:
        # 添加用户自定义的运算列名
        # TODO:没有做输入合法性检查
        for expression in user_input:
            column_name, expr = expression.split("=", 1)
            column_name = column_name.strip()
            data_names = re.findall(r"[^\+\-\*/\(\) ]+", expr)
            for data_name in data_names:
                if data_name not in self.__para_map.keys() and data_name not in self.__data_map.keys():
                    self.logger.error(f"自定义运算中的参数{data_name}不存在")
                    return False

            self.custom_calculate_map.update({column_name: expr.strip()})

    def del_custom_column(self, column_name: str) -> bool:
        if column_name in self.custom_calculate_map.keys():
            self.custom_calculate_map.pop(column_name)
            return True
        return False

    def reset():
        pass

    def reload():
        pass


def type2sqltype(data_type: str) -> str:
    if data_type == "int16":
        return "FLOAT"
    if data_type == "bit16" or data_type == "bit8":
        return "VARCHAR(255)"
    return "VARCHAR(255)"
