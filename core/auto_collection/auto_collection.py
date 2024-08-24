import time, itertools
from core.communication import Communication
from core.database.mysql_base import MySQLDatabase
from collections import deque
import threading
import re

# TODO：强行杀掉有问题的自动采集线程
DATA_TABLE_NAME = "风机数据"


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
        self.__custom_steady_state_determination: dict[str, str] = {"设定值": "设定转速", "实际值": "实际转速"}

        self.__collect_count: list[int] = [0, 0]  # 第一位是成功数量，第二位是失败数量

        self.db = database
        self.logger = self.communication.logger

    def is_stable(self) -> bool:
        return self.__stable_state

    def start_auto_collect(self) -> bool:
        """
        在一个新的线程中启动auto_collect
        """
        if not self.precheck():
            return False
        if self.__auto_running:
            self.logger.warning("正在自动采集，请勿重复启动")
            return False
        thread = threading.Thread(target=self.auto_collect)
        thread.start()
        return True

    def precheck(self) -> bool:
        data_names = self.__custom_steady_state_determination.values()
        for name in data_names:
            if (
                name not in self.communication.get_para_map().keys()
                and name not in self.communication.get_data_map().keys()
                and name not in self.communication.custom_calculate_map.keys()
            ):
                # 稳态配置中的数据项不存在于数据库中，重新配置
                self.logger.error(f"稳态判断条件中的数据项{name}不存在")
                return False
        # 检查当前配置是否存在数据表，若没有的话则创建
        table_column = self.communication.get_cureent_data_table()
        if self.db.check_exists(DATA_TABLE_NAME, table_column):
            self.db.change_current_table(DATA_TABLE_NAME, table_column)
        else:
            self.db.change_current_table(DATA_TABLE_NAME, table_column)
        self.logger.info("预检通过")
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
        :return int 当前状态
        """
        if not self.__auto_running and not self.__pause_flag and not self.__para_queue_inited:
            # 初始状态
            state = 1
        elif not self.__auto_running and not self.__pause_flag and self.__para_queue_inited:
            # 初始化数据
            state = 2
        elif self.__auto_running and not self.__pause_flag and self.__para_queue_inited:
            # 启动
            state = 3
        elif self.__auto_running and self.__pause_flag and self.__para_queue_inited:
            # 暂停
            state = 4
        else:
            state = 5
        return self.__collect_count[0], self.__collect_count[1], len(self.__para_queue), state

    def get_current_para(self) -> dict[str, any]:
        return self.communication.get_curr_para()

    def auto_collect(self) -> bool:
        if not self.__para_queue_inited:
            self.logger.error("参数队列未初始化")
            return False
        self.logger.info("自动采集启动")
        self.__auto_running = True
        self.__collect_count = [0, 0]
        # for item_para in self.__para_pool:
        # try:
        while self.__para_queue:
            self.judge_pause_status()
            if self.__stop_flag:
                break
            item_para = self.__para_queue.popleft()
            self.__stable_state = False
            tmp_para_dict = dict(zip(self.__para_vals.keys(), item_para))
            collect_data, err_handle_status, code, err = self.signal_progress(tmp_para_dict)
            # 检测到按下了停止或者出现通讯错误，那么跳出循环，以免卡在数采里面
            if self.__stop_flag or self.communication.check_error():
                break
            self.save_data(data_dict=collect_data, para_dict=tmp_para_dict, err=err)
            self.__collect_count[0 if collect_data else 1] += 1
            if not err_handle_status:
                # 清障失败，需要人工干预
                # TODO：多次出现过流情况，直接停止整个数采或者打乱数据顺序重新进行数采
                self.wait_until_no_breakdown()
        # except Exception as e:
        #     self.logger.error(f"自动采集出现异常,{e}")
        # 顺利采集完成一条数据
        self.__auto_running: bool = False
        self.clear_para()
        self.logger.info("自动采集结束")
        self.communication.close_all_device()
        return True

    def clear_para(self) -> bool:
        # 清理参数，结束一次采集循环
        if self.__auto_running:
            self.logger.warning("正在自动采集，无法清空参数,请先停止自动采集")
            return False
        self.__para_vals: dict[str, list[any]] = {}
        self.__para_queue: deque[dict[str, any]] = deque()
        self.__stable_state: bool = False
        self.__para_queue_inited: bool = False
        self.__pause_flag: bool = False
        self.__stop_flag: bool = False

        self.__collect_count: list[int] = [0, 0]  # 第一位是成功数量，第二位是失败数量
        return True

    def judge_pause_status(self):
        while self.__pause_flag:
            if self.__stop_flag:
                break
            time.sleep(0.2)

    def wait_until_no_breakdown(self):
        # 等待函数，直到读取到的数据中没有故障了才会继续向下运行
        while True:
            # 清障失败后，可以手动尝试清障，或点击停止数采按钮来停止数采
            if self.communication.find_driver("FanDriver").breakdown == False:
                self.logger.info("故障已清除，继续自动采集")
                break
            elif self.__stop_flag:
                break
            else:
                time.sleep(0.1)

    def signal_progress(self, para_dict: dict[str, any], count: int = 0) -> tuple[dict, bool, int, str]:
        """
        :return dict 采集到的稳态数据
        :return bool 清障状态，成功或失败
        :return int 失败原因，0表示无，1表示过流故障，2表示普通故障，3表示未知,4表示超时
        :return str 故障描述
        """
        # self.communication.write(para_dict)
        last = int(self.communication.find_driver("TestDevice").curr_para["测功机控制值"])
        now = int(para_dict["测功机控制值"])
        copy_para_dict = para_dict.copy()

        self.logger.info(f"当前测试的参数为{para_dict}")
        curr_time = time.time()
        time_count = 0
        steady_determination = self.steady_state_determination()
        # 稳态计时的标志
        steady_count = 0
        # avg_data = {key: [] for key in self.communication.get_data_map().keys()}
        while True:
            # 对于测功机控制数值变化过大的情况，逐步调整避免出现电机失速或者带不起来等问题
            if last > now:
                copy_para_dict["测功机控制值"] = last - 1
                last = last - 1
                self.communication.write(copy_para_dict)
                time.sleep(1)
            elif last < now:
                copy_para_dict["测功机控制值"] = last + 1
                last = last + 1
                self.communication.write(copy_para_dict)
                time.sleep(4)
            else:
                pass

            curr_data: dict[str, any] = self.communication.read()
            if self.__stable_state:
                # 稳态之后开始等待时间，一段时间后返回结果
                steady_count += 1
                time.sleep(0.05)
                if steady_count > 40:
                    final_data = self.calculate_result(curr_data, para_dict)
                    self.logger.info(f"稳定后结果为{final_data}")
                    return final_data, True, 0, ""

            # 有故障，进入故障处理模块
            if self.__stop_flag:
                return {}, False, 0, ""
            breakdown_dict = {}
            for key, value in curr_data.items():
                if "故障" in key:
                    breakdown_dict[key] = value
            for key, value in breakdown_dict.items():
                if value != "":
                    status, breakdown_type, err = self.communication.breakdown_handler.error_handle([breakdown_dict[key]])
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

            time_count += 1
            # count的判断是避免当前的稳定状态影响稳态判断,
            if steady_determination(curr_data, para_dict) and time_count > 30:
                # if self.steady_state_determination(avg_data_calculated, para_dict) and time_count > 10:
                self.__stable_state = True
                # final_data = self.calculate_result(curr_data, para_dict)
                # self.logger.info(f"稳定后结果为{final_data}")
                # return final_data, True, 0, ""
            if time.time() - curr_time > 60:
                # 超时退出，不需人工干预
                return {}, True, 4, "超时"
            time.sleep(0.05)

    def save_data(self, data_dict: dict[str, any], para_dict: dict[str, any], err: str = "") -> None:
        print(data_dict)
        print(para_dict)
        self.db.change_current_table(DATA_TABLE_NAME)
        save_data_dict = {}

        for key in para_dict.keys():
            if key in self.db.table_columns.keys():
                save_data_dict[key] = para_dict[key]
            else:
                # 数据库表中没有这一项数据
                self.logger.error(f"非法数据:{key}")

        if err:
            return self.db.insert_data([save_data_dict])

        for key in data_dict.keys():
            if key in self.db.table_columns.keys():
                save_data_dict[key] = data_dict[key]
            else:
                # 数据库表中没有这一项数据,不需要保存
                self.logger.error(f"非法数据:{key}")
        return self.db.insert_data([save_data_dict])

    def calculate_result(self, data_dict: dict[str, any], para_dict: dict[str, any]) -> dict[str, any]:
        custom_dict = {}
        for col, expr in self.communication.custom_calculate_map.items():
            expr_dict = {}
            expr_name = re.findall(r"[^\s\+\-\*\/\(\)]+", expr)
            for col_name in data_dict.keys():
                if col_name in expr_name:
                    expr_dict[col_name] = data_dict[col_name]
            for col_name in para_dict.keys():
                if col_name in expr_name:
                    expr_dict[col_name] = para_dict[col_name]
            custom_dict[col] = eval(expr, {"__builtins__": None}, expr_dict)
        data_dict.update(custom_dict)
        return data_dict

    def steady_state_determination(self, value_err: float = 5, epsilon_a: float = 2) -> bool:
        history_n = []
        # TODO：这里确认一下稳态判断的逻辑，是使用百分比的形式还是说直接使用绝对值的形式

        def is_steady(data_dict: dict[str, any], para_dict: dict[str, any]) -> bool:
            # 三大类的字符串解析可以统一起来，后面也用类似的方式去做
            # 需要对前端的配置做一个解码，可能需要一个解码函数
            set_value_name = self.__custom_steady_state_determination["设定值"]
            actual_value_name = self.__custom_steady_state_determination["实际值"]
            if set_value_name in data_dict.keys():
                set_value = data_dict[set_value_name]
            elif set_value_name in para_dict.keys():
                set_value = para_dict[set_value_name]
            elif set_value_name in self.communication.custom_calculate_map.keys():
                set_value = self.communication.custom_calculate_map[set_value_name]
            else:
                raise ValueError(f"稳态判断条件中的数据项{set_value_name}不存在")
            if actual_value_name in data_dict.keys():
                actual_value = data_dict[actual_value_name]
            elif actual_value_name in para_dict.keys():
                actual_value = para_dict[actual_value_name]
            elif actual_value_name in self.communication.custom_calculate_map.keys():
                actual_value = self.communication.custom_calculate_map[actual_value_name]
            else:
                raise ValueError(f"稳态判断条件中的数据项{actual_value_name}不存在")
            if not history_n:
                history_n.append(actual_value)
                return False
            if abs(actual_value - history_n[-1]) < epsilon_a and abs(actual_value - set_value) < value_err:
                return True
            else:
                history_n.append(actual_value)
                return False

        return is_steady

    # def steady_state_determination(self, data_dict: dict[str, any], para_dict: dict[str, any]) -> bool:

    #     # 三大类的字符串解析可以统一起来，后面也用类似的方式去做
    #     # 需要对前端的配置做一个解码，可能需要一个解码函数
    #     set_value_name = self.__custom_steady_state_determination["设定值"]
    #     actual_value_name = self.__custom_steady_state_determination["实际值"]
    #     if set_value_name in data_dict.keys():
    #         set_value = data_dict[set_value_name]
    #     elif set_value_name in para_dict.keys():
    #         set_value = para_dict[set_value_name]
    #     elif set_value_name in self.communication.custom_calculate_map.keys():
    #         set_value = self.communication.custom_calculate_map[set_value_name]
    #     else:
    #         raise ValueError(f"稳态判断条件中的数据项{set_value_name}不存在")
    #     if actual_value_name in data_dict.keys():
    #         actual_value = data_dict[actual_value_name]
    #     elif actual_value_name in para_dict.keys():
    #         actual_value = para_dict[actual_value_name]
    #     elif actual_value_name in self.communication.custom_calculate_map.keys():
    #         actual_value = self.communication.custom_calculate_map[actual_value_name]
    #     else:
    #         raise ValueError(f"稳态判断条件中的数据项{actual_value_name}不存在")

    #     return eval(solve_str)

    def set_steady_state_determination(self, value_dict: dict) -> bool:
        # 示例：目标转速 - 实际转速 < 1
        data_names = value_dict.values()
        for name in data_names:
            if (
                name not in self.communication.get_para_map().keys()
                and name not in self.communication.get_data_map().keys()
                and name not in self.communication.custom_calculate_map.keys()
            ):
                # 稳态配置中的数据项不存在于数据库中，重新配置
                self.logger.error(f"稳态判断条件中的数据项{name}不存在")
                return False

        self.__custom_steady_state_determination = value_dict
        return True

    def get_steady_state_determination(self) -> str:
        return self.__custom_steady_state_determination

    def init_para_pool(self, para_pool_dict: dict[str, dict[str, any]]) -> tuple[bool, int]:
        if self.__auto_running:
            self.logger.warning("正在自动采集，请结束或暂停后初始化参数队列")
            return False
        self.logger.info("初始化参数队列")
        # 将参数的配置转换为参数的值列表
        tmp_dict = {}
        for key, para_config in para_pool_dict.items():
            min = int(para_config.get("min", None))
            max = int(para_config.get("max", None))
            step = int(para_config.get("step", None))
            tmp_dict[key] = self.generate_test_params(min, max, step)
        para_pool_dict = tmp_dict
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
            self.logger.error(f"非法参数{error_key_list}")
            return False
        if None in self.__para_vals.values():
            self.logger.error("存在未指派的参数!")
            return False
        para_pool = itertools.product(*self.__para_vals.values())
        self.__para_queue = deque(para_pool)
        self.__para_queue_inited = True
        return True, len(self.__para_queue)

    def generate_test_params(self, min_value, max_value, step):
        # 确保步长是正数
        if step <= 0:
            raise ValueError("步长必须大于0")

        # 生成测试参数列表
        test_params = []
        param = min_value

        while param <= max_value:
            test_params.append(float(param))
            param += step

        return test_params

    # def init_para_pool_from_csv(self, para_dict: dict, data_count: int) -> bool:
    #     if self.__auto_running:
    #         self.logger.warning("正在自动采集，请结束或暂停后初始化参数队列")
    #         return False
    #     self.logger.info("初始化参数队列")
    #     self.__para_vals.clear()
    #     error_key_list: list[str] = []
    #     self.__para_vals = {key: None for key in self.communication.get_para_map().keys()}
    #     for key, val in para_dict.items():
    #         if key not in self.__para_vals.keys():
    #             error_key_list.append(key)
    #             continue
    #         self.__para_vals[key] = val
    #     if error_key_list:
    #         self.__para_vals.clear()
    #         self.logger.error(f"非法参数{error_key_list}")
    #         return False
    #     if None in self.__para_vals.values():
    #         self.logger.error("存在未指派的参数!")
    #         return False
    #     para_pool = itertools.product(*self.__para_vals.values())
    #     self.__para_queue = deque(para_pool)
    #     self.__para_queue_inited = True

    def init_para_pool_from_csv(self, para_dict_list: list[dict]) -> bool:
        try:
            if self.__auto_running:
                self.logger.warning("正在自动采集，请结束或暂停后初始化参数队列")
                return False
            self.__para_queue = deque()
            self.__para_vals = {key: 0 for key in self.communication.get_para_map().keys()}
            data_count = len(para_dict_list)
            para_dict_list_key = para_dict_list[0].keys()
            for key in self.__para_vals.keys():
                if key not in para_dict_list_key:
                    self.logger.error(f"参数{key}不存在")
                    return False

            for i in range(data_count):
                for key in self.__para_vals.keys():
                    self.__para_vals[key] = float(para_dict_list[i][key])
                self.__para_queue.append(tuple(self.__para_vals.values()))
            self.logger.info("参数队列初始化完成")
            self.__para_queue_inited = True
            return True
        except Exception as e:
            self.logger.error(f"参数队列初始化失败,{e}")
            return False

    def is_auto_running(self):
        return self.__auto_running
