import time, itertools
from typing import Union
from driver.CommunicationModule import CommunicationModule


class AutoCollector:
    def __init__(self, communication: CommunicationModule):
        self.commuication = communication
        self.__para_pool: itertools.product
        self.__para_pool_vals: dict[str, list[any]] = {}
        self.__stable_state: bool = False
        self.__para_pool_inited: bool = False
        self.__auto_running: bool = False
        pass

    def is_stable(self) -> bool:
        return self.__stable_state

    def auto_collect(self) -> bool:
        if not self.__para_pool_inited:
            print("参数池未初始化")
            return False
        print("自动采集启动")
        self.__auto_running = True
        for item_para in self.__para_pool:
            self.__stable_state = False
            tmp_para_dict = dict(zip(self.__para_pool_vals.keys(), item_para))
            self.commuication.write(tmp_para_dict)
            print("当前测试的参数为", tmp_para_dict)
            self.wait_stable()
            print("稳定后结果为", self.commuication.read())
        print("自动采集结束")
        self.__auto_running = False
        return True

    def wait_stable(self) -> None:
        time.sleep(5)
        self.__stable_state = False
        pass

    def init_para_pool(self, para_pool_dict: dict[str, list[any]]) -> bool:
        if self.__auto_running:
            print("正在自动采集，请结束或暂停后初始化参数池")
            return False
        print("初始化参数池")
        self.__para_pool_vals.clear()
        error_key_list: list[str] = []
        self.__para_pool_vals = {key: None for key in self.commuication.get_para_map().keys()}
        for key, val in para_pool_dict.items():
            if key not in self.__para_pool_vals.keys():
                error_key_list.append(key)
                continue
            self.__para_pool_vals[key] = val
        if error_key_list:
            self.__para_pool_vals.clear()
            print("非法参数", *error_key_list)
            return False
        if None in self.__para_pool_vals.values():
            print("存在未指派的参数!")
            return False
        self.__para_pool = itertools.product(*self.__para_pool_vals.values())
        self.__para_pool_inited = True
        return True

    def is_auto_running(self):
        return self.__auto_running
