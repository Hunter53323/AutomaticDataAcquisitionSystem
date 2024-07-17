import time, itertools
from core.communication import Communication
from core.database.mysql_base import MySQLDatabase
from collections import deque
import threading


class AutoCollection:
    def __init__(self, communication: Communication, database: MySQLDatabase):
        self.communication = communication
        self.__para_vals: dict[str, list[any]] = {}
        self.__para_queue: deque[dict[str, any]] = deque()
        self.__stable_state: bool = False
        self.__para_queue_inited: bool = False
        self.__auto_running: bool = False
        self.__pause_flag: bool = False
        self.__stop_flag: bool = False

        self.__collect_count: list[int] = [0, 0]  # 第一位是成功数量，第二位是失败数量

        self.db = database
        pass

    def is_stable(self) -> bool:
        return self.__stable_state

    def start_auto_collect(self) -> bool:
        """
        在一个新的线程中启动auto_collect
        """
        if self.__auto_running:
            print("正在自动采集...")
            return False
        thread = threading.Thread(target=self.auto_collect)
        thread.start()
        return True

    def pause_auto_collect(self) -> bool:
        if not self.__auto_running:
            return False
        self.__pause_flag = True
        return True

    def continue_auto_collect(self) -> bool:
        if not self.__auto_running:
            return False
        self.__pause_flag = False
        return True

    def stop_auto_collect(self) -> bool:
        if not self.__auto_running:
            return False
        self.__stop_flag = True
        return True

    def get_current_progress(self) -> tuple[int, int, int, bool]:
        """
        :return int 成功采集数量
        :return int 失败采集数量
        :return int 剩余采集数量
        :return bool 是否正在自动采集
        """
        return self.__collect_count[0], self.__collect_count[1], len(self.__para_queue), self.__auto_running

    def get_current_para(self) -> dict[str, any]:
        return self.communication.get_curr_para()

    def auto_collect(self) -> bool:
        if not self.__para_queue_inited:
            print("参数队列未初始化")
            return False
        print("自动采集启动")
        self.__auto_running = True
        self.__collect_count = [0, 0]
        # for item_para in self.__para_pool:
        while self.__para_queue:
            if self.__stop_flag:
                break
            self.judge_pause_status()
            item_para = self.__para_queue.popleft()
            self.__stable_state = False
            tmp_para_dict = dict(zip(self.__para_vals.keys(), item_para))
            collect_data, err_handle_status, code, err = self.signal_progress(tmp_para_dict)
            self.save_data(data_dict=collect_data, para_dict=tmp_para_dict, err=err)
            self.__collect_count[0 if collect_data else 1] += 1
            if not err_handle_status:
                # 清障失败，需要人工干预
                # 故障预警
                self.communication.breakdown_handler.breakdown_warning(code)
                self.wait_until_no_breakdown()
            # 顺利采集完成一条数据
        self.clear_para()
        print("自动采集结束")
        return True

    def clear_para(self):
        # 清理参数，结束一次采集循环
        self.__para_vals: dict[str, list[any]] = {}
        self.__para_queue: deque[dict[str, any]] = deque()
        self.__stable_state: bool = False
        self.__para_queue_inited: bool = False
        self.__auto_running: bool = False
        self.__pause_flag: bool = False
        self.__stop_flag: bool = False

        self.__collect_count: list[int] = [0, 0]  # 第一位是成功数量，第二位是失败数量

    def judge_pause_status(self):
        while self.__pause_flag:
            time.sleep(0.2)

    def wait_until_no_breakdown(self):
        # 等待函数，直到读取到的数据中没有故障了才会继续向下运行
        while True:
            curr_data: dict[str, any] = self.communication.read()
            if curr_data["breakdown"] != []:
                time.sleep(0.1)
                continue
            else:
                print("故障已清除，继续自动采集")

    def signal_progress(self, para_dict: dict[str, any], count: int = 0) -> tuple[dict, bool, int, str]:
        """
        :return dict 采集到的稳态数据
        :return bool 清障状态，成功或失败
        :return int 失败原因，0表示无，1表示过流故障，2表示普通故障，3表示未知,4表示超时
        :return str 故障描述
        """
        self.communication.write(para_dict)
        print("当前测试的参数为", para_dict)
        curr_time = time.time()
        count = 0
        while True:
            curr_data: dict[str, any] = self.communication.read()
            # 有故障，进入故障处理模块
            if curr_data["breakdown"] != [] and curr_data["breakdown"] != 0:
                status, breakdown_type, err = self.communication.breakdown_handler.error_handle(curr_data["breakdown"])
                if count == 3:
                    # 错误尝试次数过多，直接退出
                    return {}, status, breakdown_type, err
                if breakdown_type == 1:
                    # 过流故障，直接退出
                    return {}, status, breakdown_type, err
                elif breakdown_type == 2:
                    # 普通故障，尝试清障
                    return self.signal_progress(para_dict, count + 1)
                else:
                    # 无故障
                    pass
            # 故障处理完毕，正常运行
            count += 1
            # if abs(curr_data["actual_speed"] - curr_data["target_speed"]) < 2:
            if count == 30:  # TODO:测试阶段使用sleep，后续启用真实的数据采集
                self.__stable_state = True
                final_data = self.calculate_result(curr_data)
                print("稳定后结果为", curr_data)
                return final_data, True, 0, ""
            if time.time() - curr_time > 60:
                # 超时退出，不需人工干预
                return {}, True, 4, "超时"
            time.sleep(0.05)

    def save_data(self, data_dict: dict[str, any], para_dict: dict[str, any], err: str = "") -> None:
        pass

    def calculate_result(self, data_dict: dict[str, any]) -> dict[str, any]:
        pass

    def init_para_pool(self, para_pool_dict: dict[str, list[any]]) -> bool:
        if self.__auto_running:
            print("正在自动采集，请结束或暂停后初始化参数队列")
            return False
        print("初始化参数队列")
        self.__para_vals.clear()
        error_key_list: list[str] = []
        self.__para_vals = {key: None for key in self.communication.get_para_map().keys()}
        for key, val in para_pool_dict.items():
            if key not in self.__para_vals.keys():
                error_key_list.append(key)
                continue
            self.__para_vals[key] = val
        if error_key_list:
            self.__para_vals.clear()
            print("非法参数", *error_key_list)
            return False
        if None in self.__para_vals.values():
            print("存在未指派的参数!")
            return False
        para_pool = itertools.product(*self.__para_vals.values())
        self.__para_queue = deque(para_pool)
        self.__para_queue_inited = True
        return True

    def init_para_pool_from_csv(self, para_dict_list: list[dict]) -> bool:
        if self.__auto_running:
            self.logger.warning("正在自动采集，请结束或暂停后初始化参数队列")
            return False
        self.__para_vals = {key: 0 for key in self.communication.get_para_map().keys()}
        data_count = len(para_dict_list)
        para_dict_list_key = para_dict_list[0].keys()
        for key in self.__para_vals.keys():
            if key not in para_dict_list_key:
                self.logger.error(f"参数{key}不存在")
                return False

        for i in range(data_count):
            for key in self.__para_vals.keys():
                self.__para_vals[key] = para_dict_list[i][key]
            self.__para_queue.append(tuple(self.__para_vals.values()))

        self.__para_queue_inited = True


    def is_auto_running(self):
        return self.__auto_running
