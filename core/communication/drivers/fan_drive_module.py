# -*- coding:utf-8 -*-
import json
from typing import Tuple

import serial
from serial.serialutil import SerialTimeoutException
from .driver_base import DriverBase
from .frame import serial_frame
import time
import copy

serial_port = "COM9"  # 请替换为您的串行端口
serial_baudrate = 9600  # 根据实际情况设置波特率
serial_parity = "N"  # None表示无校验
serial_stopbits = 1  # 停止位
serial_bytesize = 8  # 数据位


class FanDriver(DriverBase):
    def __init__(self, device_name: str, **kwargs):  # para_list控制列表，data_list查询数据列表
        super().__init__(device_name)
        # 协议要求，未赋值的参数为0
        for key in self.curr_para:
            self.curr_para[key] = 0
        self.cpu = None
        self.port = None
        self.device_address = None
        self.is_set_data = False
        # 帧声明,及默认初始化
        self.query_f = serial_frame.Framer()
        self.control_f = serial_frame.Framer()
        self.ack_query_f = serial_frame.Framer()
        self.ack_control_f = serial_frame.Framer()
        self.default_frame()
        # 解析传参
        for key, value in kwargs.items():
            if key == "cpu":
                if value != "M0" and value != "M4":
                    self.logger.error("Invalid cpu value")
                    raise ValueError("Invalid cpu value")
                self.cpu = value
            if key == "port":
                if not isinstance(value, str):
                    self.logger.error("Invalid port value")
                    raise ValueError("Invalid port value")
                self.port = value
            if key == "device_address":
                if not isinstance(value, str):
                    self.logger.error("Invalid device_address value")
                    raise ValueError("Invalid device_address value")
                self.device_address = value

        self.hardware_para = ["device_address", "cpu"]
        self.command = "控制命令"

        self.ser: serial.Serial = serial.Serial(
            baudrate=serial_baudrate, parity=serial_parity, stopbits=serial_stopbits, bytesize=serial_bytesize,
            timeout=10
        )

    def set_F_header(self, send_header: str, rev_header: str):
        if not isinstance(send_header, str):
            self.logger.error(f"Invalid send header value{send_header}")
            raise ValueError(f"Invalid send header value{send_header}")
        self.query_f.set_header(send_header)
        self.control_f.set_header(send_header)
        if not isinstance(rev_header, str):
            self.logger.error(f"Invalid rev header value{rev_header}")
            raise ValueError(f"Invalid rev header value{rev_header}")
        self.ack_query_f.set_header(rev_header)
        self.ack_control_f.set_header(rev_header)

    def set_F_addr(self, addr: str):
        if not isinstance(addr, str):
            self.logger.error(f"Invalid addr value{addr}")
            raise ValueError(f"Invalid addr value{addr}")
        self.query_f.set_addr(addr)
        self.control_f.set_addr(addr)

    def set_F_tailor(self, send_tailor: str, rev_tailor: str):
        if not isinstance(send_tailor, str):
            self.logger.error(f"Invalid send tail value{send_tailor}")
            raise ValueError(f"Invalid send tail value{send_tailor}")
        self.query_f.set_tail(send_tailor)
        self.control_f.set_tail(send_tailor)
        if not isinstance(rev_tailor, str):
            self.logger.error(f"Invalid rev tail value{rev_tailor}")
            raise ValueError(f"Invalid rev tail value{rev_tailor}")
        self.ack_query_f.set_tail(rev_tailor)
        self.ack_control_f.set_tail(rev_tailor)

    def set_device_cpu(self, cpu: str) -> tuple[bool, None] | tuple[bool, Exception]:
        try:
            if not isinstance(cpu, str):
                self.logger.error(f"Invalid cpu value{cpu}")
                raise ValueError(f"Invalid cpu value{cpu}")
            self.cpu = cpu
            return True, None
        except Exception as e:
            return False, e

    def set_device_address(self, value: str):
        try:
            if not isinstance(value, str):
                self.logger.error(f"Invalid device_address value{value}")
                raise ValueError(f"Invalid device_address value{value}")
            self.device_address = value
            return True, None
        except Exception as e:
            return False, e

    def set_port(self, value) -> tuple[bool, None] | tuple[bool, Exception]:
        try:
            if not isinstance(value, str):
                self.logger.error(f"Invalid port value{value}")
                raise ValueError(f"Invalid port value{value}")
            self.port = value
            return True, None
        except Exception as e:
            return False, e

    def default_frame(self):
        # 初始化命令码
        self.control_f.set_cmd("01")
        self.ack_control_f.set_cmd("01")
        self.query_f.set_cmd("02")
        self.ack_query_f.set_cmd("02")
        # 默认接收帧头5A，默认发送帧头A5
        self.ack_query_f.set_header("5A")
        self.ack_control_f.set_header("5A")
        # 默认接收帧尾A5，默认发送帧头5A
        self.ack_query_f.set_tail("A5")
        self.ack_control_f.set_tail("A5")
        # 默认接收地址FF，默认发送地址01
        self.query_f.set_addr("01")
        self.control_f.set_addr("01")
        # 默认控制应答data
        self.set_data(index=1, name="send_result", type="bit8", size=1, formula="", f_name="ack_control_f")
        # 默认一期配置
        self.cpu_default_config()

    def cpu_default_config(self):
        FB, VB, IB, Cofe1, Cofe2, Cofe3, Cofe4, Cofe5 = self.get_cpu_paras()
        self.set_data(index=1, name="目标转速", type="int16", size=2,
                      formula=f"real_data=raw_data* {FB} * {Cofe1} / {Cofe2}", f_name=self.ack_query_f)
        self.set_data(index=2, name="实际转速", type="int16", size=2,
                      formula=f"real_data=raw_data* {FB} * {Cofe1} / {Cofe2}", f_name=self.ack_query_f)
        self.set_data(index=3, name="直流母线电压", type="int16", size=2,
                      formula=f"real_data=raw_data* {VB} / {Cofe2}", f_name=self.ack_query_f)
        self.set_data(index=4, name="U相电流有效值", type="int16", size=2,
                      formula=f"real_data=raw_data* {IB} / {Cofe2} / {Cofe5}", f_name=self.ack_query_f)
        self.set_data(
            index=5, name="功率", type="int16", size=2,
            formula=f"real_data=raw_data* {IB} * {VB} * {Cofe3} / {Cofe4} / {Cofe2} / {Cofe5}", f_name=self.ack_query_f
        )
        self.set_data(index=6, name="故障", type="bit16", size=2, formula="", f_name=self.ack_query_f)

        self.set_data(index=1, name="控制命令", type="bit8", size=1, formula="real_data=raw_data",
                      f_name=self.control_f)
        self.set_data(index=2, name="给定转速", type="int16", size=2, formula="real_data=raw_data",
                      f_name=self.control_f)
        self.set_data(index=3, name="速度环补偿带宽", type="int16", size=2, formula="real_data=raw_data*10",
                      f_name=self.control_f)
        self.set_data(index=4, name="电流环带宽", type="int16", size=2, formula="real_data=raw_data",
                      f_name=self.control_f)
        self.set_data(index=5, name="观测器补偿带宽", type="int16", size=2, formula="real_data=raw_data*100",
                      f_name=self.control_f)

    def set_data(self, index: int, name: str, type: str, size: int, formula: str, f_name) -> bool:
        if f_name == "ack_query_f":
            state, e = self.ack_query_f.set_data(index=index, name=name, type=type, size=size, formula=formula)
            if state:
                self.curr_para[name] = 0
                return True
            else:
                return False
        elif f_name == "control_f":
            state, e = self.control_f.set_data(index=index, name=name, type=type, size=size, formula=formula)
            if state:
                self.curr_para[name] = 0
                return True
            else:
                return False
        elif f_name == "query_f":
            state, e = self.query_f.set_data(index=index, name=name, type=type, size=size, formula=formula)
            if state:
                return True
            else:
                return False
        elif f_name == "ack_control_f":
            state, e = self.ack_control_f.set_data(index=index, name=name, type=type, size=size, formula=formula)
            if state:
                return True
            else:
                return False

    def updata_F_data(self, f_name: str, index: int, name: str, type: str, size: int, formula: str) -> tuple[
                                                                                                           bool, None] | \
                                                                                                       tuple[
                                                                                                           bool, Exception]:
        try:
            state, e = self.delete_F_data(f_name=f_name, index=index)
            if not state:
                raise e
            state, e = self.set_data(index=index, name=name, type=type, size=size, formula=formula, f_name=f_name)
            if not state:
                raise e
            return True, None
        except Exception as e:
            self.logger.error(e)
            return False, e

    def delete_F_data(self, f_name: str, index: int):
        try:
            if f_name == "query_f":
                self.query_f.data.pop(index)
            elif f_name == "control_f":
                self.curr_para.pop(self.control_f.data[index].name)
                self.control_f.data.pop(index)
            elif f_name == "ack_query_f":
                self.curr_data.pop(self.ack_query_f.data[index].name)
                self.curr_data.pop(index)
            elif f_name == "ack_control_f":
                self.ack_control_f.data.pop(index)
            return True, None
        except Exception as e:
            return False, e

    def connect(self) -> bool:
        if self.cpu is None:
            self.logger.error("self.cpu is None")
            return False
        if self.port is None:
            self.logger.error("self.port is None")
            return False
        if self.ser.port != self.port:
            self.ser.port = self.port
        return self.__connect()

    def __connect(self) -> bool:
        if self.conn_state:
            self.logger.info("self.ser is already open")
            return True
        self.ser.open()
        if self.ser.is_open:
            self.conn_state = True
            self.logger.info("self.ser open true")
            return True
        else:
            self.logger.error("self.ser open false")
            return False

    def disconnect(self) -> bool:
        self.ser.close()
        if self.ser.is_open:
            self.logger.error("self.ser close false")
            return False
        else:
            self.conn_state = False
            self.logger.info("self.ser close true")
            return True

    def __serwrite(self, byte_data: bytes, count: int = 0) -> tuple[bool, str]:
        """
        自定义的写操作，最多尝试重写三次
        """
        try:
            self.ser.write(byte_data)
            # self.logger.info(f"ser write context:{byte_data.hex()}")
            return True, ""
        except SerialTimeoutException as e:
            # print(e)
            self.logger.error(f"ser write error:{e},count:{count}")
            return False, "Timeout"
        except Exception as e:
            self.logger.error(f"ser write error:{e},count:{count}")
            if count == 3:
                # print(e)
                return False, "Unknown error"
            return self.__serwrite(byte_data, count=count + 1)

    def read_all(self, read_count: int = 0) -> bool:
        """
        查询指令
        """
        query_byte = self.query_f.encode_framer()
        self.logger.debug(f"查询指令:{query_byte.hex()}")
        # 写以及写出错的处理
        write_status, err = self.__serwrite(query_byte)
        if not write_status:
            self.logger.error(f"查询指令写入串口报错! reason:{err},查询指令:{query_byte.hex()}")
            return False

        # 查询处理
        response, status = self.read_msg()
        if not status:
            self.logger.error(f"查询指令读取串口数据报错!,count:{read_count}")
            if read_count == 3:
                return False
            return self.read_all(read_count=read_count + 1)
        self.logger.debug(f"查询回复:{response.hex()}")

        # 检测收到的数据是否是预期的数据，否则报错
        state, e = self.ack_query_f.cofirm_framer(response)
        if not state:
            self.logger.error(f"查询回复解析报错{e}")
            if read_count == 3:
                return False
            return self.read_all(read_count=read_count + 1)

        # 数据检查完毕后开始读取数据
        self.curr_data = self.ack_query_f.get_data()

        # 故障处理
        if "故障" in self.curr_data:
            if self.curr_data["故障"] != 0:
                pass  # 故障处理未写
                # self.logger.info(f"查询到故障! 故障码:{', '.join(str(breakdown) for breakdown in breakdowns)}")
                self.run_state = False
                self.breakdown = True
        else:
            self.logger.error("error! 未查询到故障信息，请检查查询回复报文设置是否正确！")
        return True

    def read_msg(self) -> tuple[bytes, bool]:
        try:
            while self.ser.in_waiting < 4:
                time.sleep(0.005)
            recv = self.ser.read(4)
            while self.ser.in_waiting < recv[3] + 2:
                time.sleep(0.005)
            recv = recv + self.ser.read(recv[3] + 2)
            return recv, True
        except Exception as e:
            self.logger.error(f"error:{e}, recv:{recv}")
            self.logger.error(f"error_data:{self.ser.read_all()}")
            return b"", False

    def handle_breakdown(self, breakdown: int) -> bool:
        try:
            if breakdown == 1:
                self.logger.info(f"故障为过流故障! ")
            elif breakdown == 2:
                self.logger.info(f"故障为普通故障! ")
                # 过流处理逻辑
            para_dict = {
                "fan_command": "clear_breakdown",
                "set_speed": 0,
                "speed_loop_compensates_bandwidth": 0,
                "current_loop_compensates_bandwidth": 0,
                "observer_compensates_bandwidth": 0,
            }
            if self.write(para_dict):
                self.logger.info(f"故障清除成功!")
            else:
                raise Exception(f"故障清除失败！")
            return True
        except Exception as e:
            self.logger.error(f"error:{e}")
            return False

    def load_config(self, F_config: dict) -> tuple[bool, None] | tuple[bool, Exception]:
        try:
            for key, value in F_config.items():
                if key == "query_f":
                    self.query_f.reset_all()
                    self.query_f.load_framer(json.loads(value))
                elif key == "control_f":
                    self.control_f.reset_all()
                    self.control_f.load_framer(json.loads(value))
                elif key == "ack_query_f":
                    self.ack_query_f.reset_all()
                    self.ack_query_f.load_framer(json.loads(value))
                elif key == "ack_control_f":
                    self.ack_control_f.reset_all()
                    self.ack_control_f.load_framer(json.loads(value))
            return True, None
        except Exception as e:
            self.logger.error(f"风机帧配置导入error！{e}")
        return False, e

    def export_config(self):
        return {
            "query_f": json.dumps(self.pre_dict(self.query_f.export_framer())),
            "control_f": json.dumps(self.pre_dict(self.control_f.export_framer())),
            "ack_query_f": json.dumps(self.pre_dict(self.ack_query_f.export_framer())),
            "ack_control_f": json.dumps(self.pre_dict(self.ack_control_f.export_framer())),
        }

    def get_database_table(self) -> dict[str, str]:
        all_data = {}
        for _, value in self.ack_query_f.data.items():
            all_data[value.name] = value.type
        for _, value in self.control_f.data.items():
            all_data[value.name] = value.type
        return all_data

    # 转换帧对象的变量中byte为str
    def pre_dict(self, obj: dict):
        dict_obj = {}
        # 遍历对象的属性
        for key, value in obj.items():
            # 如果值是字节串，则转换为十六进制字符串
            if isinstance(value, bytes):
                dict_obj[key] = value.hex()
            else:
                dict_obj[key] = value
        return dict_obj

    def write(self, para_dict: dict[str, any]) -> bool:
        if not self.check_writable():
            self.logger.error(f"串口不可写!")
            return False
        self.__iswriting = True
        status = self.write_execute(para_dict)
        self.__iswriting = False
        return status

    def set_default(self):
        self.logger.debug("使用默认帧格式")
        self.is_set_data = True

    def write_execute(self, para_dict: dict[str, int], write_count: int = 1) -> bool:
        """
        控制指令
        """
        if not self.is_set_data:
            self.logger.error("控制帧还未定义不可写")
            return False
        # 有无控制命令
        if self.command in para_dict:
            command = para_dict[self.command]
        else:
            command = "write"
        # 参数不全的情况下，需要将以往的参数补充上
        if write_count == 1:
            para_dict.update({key: self.curr_para[key] for key in self.curr_para if key not in para_dict})

        if command == "start" or command == "启动":
            command = 1
        elif command == "stop" or command == "停止":
            command = 2
        elif command == "clear_breakdown" or command == "清障":
            command = 4
        else:
            command = 0

        para_dict[self.command] = command
        for key, value in para_dict.items():
            # print(key,value)
            if key == "控制命令":
                self.control_f.gen_data(key, command)
            else:
                self.control_f.gen_data(key, value)

        write_bytes = self.control_f.encode_framer()
        self.logger.info(f"控制指令:{write_bytes.hex()}")
        # self.ser.write(write_bytes)
        # 写以及写出错的处理
        write_status, err = self.__serwrite(write_bytes)
        if not write_status:
            self.logger.error(f"控制指令写入串口报错！ 控制指令:{write_bytes.hex()},count:{write_count}")
            return False

        response, status = self.read_msg()
        if not status:
            self.logger.error(f"控制回复读取串口数据报错!,count:{write_count}")
            if write_count == 3:
                return False
            return self.read_all(read_count=write_count + 1)
        self.logger.debug(f"控制回复:{response.hex()}")

        # 检测收到的数据是否是预期的数据，否则报错
        state, e = self.ack_control_f.cofirm_framer(response)
        if not state:
            self.logger.error(f"控制回复报错！{e}")
            if write_count == 3:
                return False
            return self.write_execute(para_dict, write_count=write_count + 1)

            # 确认读写操作正确后，修改参数表
        if command == 1:
            self.run_state = True
        elif command == 2:
            self.run_state = False
        elif command == 4:
            self.breakdown = False

        for key in self.curr_para:
            self.curr_para[key] = para_dict[key]
        return True

    def get_cpu_paras(self) -> tuple[int, int, int, int, int, int, int, int]:
        if self.cpu == "M0":
            return 25, 380, 2, 60, 32768, 3, 2, 1
        elif self.cpu == "M4":
            return 1, 1, 1, 1, 1, 1, 1, 1000
        return 1, 1, 1, 1, 1, 1, 1, 1

    def update_hardware_parameter(self, para_dict: dict[str, any]) -> bool:
        for key in para_dict.keys():
            if key not in ["device_address", "cpu", "port"]:
                # raise ValueError("Unknown parameter")
                return False
        for key, value in para_dict.items():
            if key == "device_address":
                if not self.set_device_address(value)[0]:
                    return False
            elif key == "cpu":
                if not self.set_device_cpu(value)[0]:
                    return False
            elif key == "port":
                if not self.set_port(value)[0]:
                    return False
            else:
                return False
        return True

    def get_hardware_parameter(self) -> dict[str, any]:
        return {"device_address": self.device_address, "cpu": self.cpu, "port": self.port}


if __name__ == "__main__":
    fan_driver = FanDriver("Fan", device_address="01", cpu="M0", port=serial_port)
    # fan_driver.update_hardware_parameter({"device_address": "034", "cpu": "M0", "port": "COM6"})
    # print(fan_driver.get_hardware_parameter())

    fan_driver.connect()
    # fan_driver.read_all()
    # print(fan_driver.ack_query_f.get_data())
    # fan_driver.control_f.set_data(index=6, name="new", type="int16", size=2, formula="real_data=raw_data*100")
    # json_dict = fan_driver.export_config()
    # print(json_dict)
    # fan_driver2 = FanDriver("Fan2", [], [], device_address="01", cpu="M0", port=serial_port)
    # fan_driver2.load_config(json_dict)
    # print(fan_driver2.export_config())

    para_dict = {
        "控制命令": "start",
        "给定转速": 1,
        "速度环补偿带宽": 2,
        "电流环带宽": 3,
        "观测器补偿带宽": 4,
    }
    fan_driver.set_default()
    fan_driver.write(para_dict)
