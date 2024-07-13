from .drivers.driver_base import DriverBase
from .exception_handling import BreakdownHanding


class Communication:
    def __init__(self) -> None:
        self.drivers: list[DriverBase] = []
        self.__para_map: dict[str, DriverBase] = {}
        self.__data_map: dict[str, DriverBase] = {}
        self.breakdown_handler = BreakdownHanding()
        pass

    def __update_map(self, driver: DriverBase):
        self.__para_map.update({key: driver for key in driver.curr_para.keys()})
        self.__data_map.update({key: driver for key in driver.curr_data.keys()})

    def write(self, para_dict: dict[str, any]) -> bool:
        for driver in self.drivers:
            if driver.breakdown == True:
                print(driver.device_name, "发生故障，请先处理故障")
                return False
        tmp_dict: dict[DriverBase, dict[str, any]] = {}
        error_key_list: list[str] = []
        for key, val in para_dict.items():
            if key not in self.__para_map.keys():
                error_key_list.append(key)
                continue
            if self.__para_map[key] not in tmp_dict.keys():
                tmp_dict[self.__para_map[key]] = {}
            tmp_dict[self.__para_map[key]].update({key: val})
        if error_key_list:
            print("非法参数", *error_key_list)
            return False
        flag = True
        for key, val in tmp_dict.items():
            flag = flag & key.write(val)
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
            print("非法参数", *error_key_list)
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
            print("非法参数", *error_key_list)
        for key, val in tmp_dict.items():
            result = {**result, **key.get_curr_para(val)}
        return result

    def register_device(self, driver: DriverBase) -> bool:
        self.drivers.append(driver)
        self.__update_map(driver)
        self.breakdown_handler.add_driver(driver)

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
        return flag

    def get_para_map(self) -> dict[str, DriverBase]:
        return self.__para_map

    def get_data_map(self) -> dict[str, DriverBase]:
        return self.__data_map

    def stop_read_all(self) -> bool:
        flag = True
        for driver in self.drivers:
            flag = flag & driver.stop_read_all()
        return flag

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
                        print("非法参数", key)
                for key in err_key:
                    para_dict.pop(key)
                return driver.update_hardware_parameter(para_dict)
        return False

    def get_hardware_parameter(self, device_name: str) -> dict[str, any]:
        for driver in self.drivers:
            if driver.device_name == device_name:
                return driver.get_hardware_parameter()
        return {}
