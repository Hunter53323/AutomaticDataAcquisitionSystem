# -*- coding:utf-8 -*-
import json
from typing import Tuple, Any

import serial
from serial.serialutil import SerialTimeoutException
from .driver_base import DriverBase
from .frame import serial_frame
import time
import copy

serial_port = "COM9"  # 请替换为您的串行端口
serial_baudrate = 115200  # 根据实际情况设置波特率
serial_parity = "N"  # None表示无校验
serial_stopbits = 1  # 停止位
serial_bytesize = 8  # 数据位


class FanDriver(DriverBase):
    def __init__(self, device_name: str, **kwargs):  # para_list控制列表，data_list查询数据列表
        super().__init__(device_name)
        # 协议要求，未赋值的参数为0
        for key in self.curr_para:
            self.curr_para[key] = 0
        self.cpu = "M0"
        self.port = serial_port
        self.serial_baudrate = serial_baudrate
        self.device_address = None
        self.is_set_data = False
        # 帧声明,及默认初始化
        self.query_f = serial_frame.Framer()
        self.control_f = serial_frame.Framer()
        self.ack_query_f = serial_frame.Framer()
        self.ack_control_f = serial_frame.Framer()
        self.default_frame()

        self.hardware_para = ["port", "cpu", "baudrate"]
        self.command = "控制命令"

        self.ser: serial.Serial = serial.Serial(
            baudrate=serial_baudrate, parity=serial_parity, stopbits=serial_stopbits, bytesize=serial_bytesize, timeout=10
        )

    def set_F_header(self, send_header: str, rev_header: str):
        self.query_f.set_header(send_header)
        self.control_f.set_header(send_header)
        self.ack_query_f.set_header(rev_header)
        self.ack_control_f.set_header(rev_header)

    def set_F_addr(self, addr: str):
        self.query_f.set_addr(addr)
        self.control_f.set_addr(addr)

    def set_F_tailor(self, send_tailor: str, rev_tailor: str):
        self.query_f.set_tail(send_tailor)
        self.control_f.set_tail(send_tailor)
        self.ack_query_f.set_tail(rev_tailor)
        self.ack_control_f.set_tail(rev_tailor)

    def set_device_cpu(self, cpu: str) -> None:
        # TODO: 当前的cpu配置仅支持默认配置的切换，在非默认配置的时候不做支持
        self.cpu = cpu
        self.logger.info(f"设置CPU为{cpu}")
        self.cpu_default_config()

    def set_port(self, value: str) -> None:
        self.port = value
        self.logger.info(f"设置串口为{value}")

    def set_baudrate(self, value: int) -> None:
        self.serial_baudrate = value
        self.ser.baudrate = value
        self.logger.info(f"设置波特率为{value}")

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
        self.cpu_default_config(True)

    def cpu_default_config(self, init: bool = False):
        FB, VB, IB, Cofe1, Cofe2, Cofe3, Cofe4, Cofe5 = self.get_cpu_paras()
        self.updata_F_data(
            index=1, name="目标转速", type="int16", size=2, formula=f"real_data=raw_data* {FB} * {Cofe1} / {Cofe2}",
            f_name="ack_query_f", init=init
        )
        self.updata_F_data(
            index=2, name="实际转速", type="int16", size=2, formula=f"real_data=raw_data* {FB} * {Cofe1} / {Cofe2}",
            f_name="ack_query_f", init=init
        )
        self.updata_F_data(index=3, name="直流母线电压", type="int16", size=2,
                           formula=f"real_data=raw_data* {VB} / {Cofe2}", f_name="ack_query_f", init=init)
        self.updata_F_data(
            index=4, name="U相电流有效值", type="int16", size=2,
            formula=f"real_data=raw_data* {IB} / {Cofe2} / {Cofe5}", f_name="ack_query_f", init=init
        )
        self.updata_F_data(
            index=5,
            name="功率",
            type="int16",
            size=2,
            formula=f"real_data=raw_data* {IB} * {VB} * {Cofe3} / {Cofe4} / {Cofe2} / {Cofe5}",
            f_name="ack_query_f", init=init
        )
        self.updata_F_data(index=6, name="故障", type="bit16", size=2, formula="", f_name="ack_query_f", init=init)

        self.curr_data = {"目标转速": 0, "实际转速": 0, "直流母线电压": 0, "U相电流有效值": 0, "功率": 0, "故障": 0}

        self.updata_F_data(index=1, name="控制命令", type="bit8", size=1, formula="real_data=raw_data",
                           f_name="control_f", init=init)
        self.updata_F_data(index=2, name="设定转速", type="int16", size=2, formula="real_data=raw_data",
                           f_name="control_f", init=init)
        self.updata_F_data(index=3, name="速度环补偿系数", type="int16", size=2, formula="real_data=raw_data*10",
                           f_name="control_f", init=init)
        self.updata_F_data(index=4, name="电流环带宽", type="int16", size=2, formula="real_data=raw_data",
                           f_name="control_f", init=init)
        self.updata_F_data(index=5, name="观测器补偿系数", type="int16", size=2, formula="real_data=raw_data*100",
                           f_name="control_f", init=init)
        # TODO: realdata表示给用户展示或者用户输入的数据，rawdata表示实际发送或接受的数据
        self.curr_para = {"控制命令": 0, "设定转速": 0, "速度环补偿系数": 0, "电流环带宽": 0, "观测器补偿系数": 0}

        self.set_default()

    def set_data(self, index: int, name: str, type: str, size: int, formula: str, f_name: str,name_list:list) -> tuple[bool, None] | tuple[bool, Any]:
        if f_name == "ack_query_f":
            state, e = self.ack_query_f.set_data(index=index, name=name, type=type, size=size, formula=formula,breakdowns=name_list)
            if state:
                self.curr_data[name] = 0
                return True, None
            else:
                return False, e
        elif f_name == "control_f":
            state, e = self.control_f.set_data(index=index, name=name, type=type, size=size, formula=formula)
            if state:
                self.curr_para[name] = 0
                return True, None
            else:
                return False, e
        elif f_name == "query_f":
            state, e = self.query_f.set_data(index=index, name=name, type=type, size=size, formula=formula)
            if state:
                return True, None
            else:
                return False, e
        elif f_name == "ack_control_f":
            state, e = self.ack_control_f.set_data(index=index, name=name, type=type, size=size, formula=formula)
            if state:
                return True, None
            else:
                return False, e

    def updata_F_data(self, f_name: str, index: int, name: str, type: str, size: int, formula: str,
                      init: bool = False) -> tuple[bool, None] | tuple[bool, Exception]:
        try:
            state1 = True
            e1 = None
            if not init:
                state1, e1 = self.delete_F_data(f_name=f_name, index=index)
            state2, e2 = self.set_data(index=index, name=name, type=type, size=size, formula=formula, f_name=f_name)
            if not (state1 and state2):
                raise Exception(f"删除帧：{e1},增加帧：{e2}")
            return True, None
        except Exception as e:
            self.logger.error(e)
            return False, e

    def delete_F_data(self, f_name: str, index: int) -> tuple[bool, None] | tuple[bool, Exception]:
        try:
            if f_name == "query_f":
                self.query_f.data.pop(index)
            elif f_name == "control_f":
                # print(self.curr_para)
                self.curr_para.pop(self.control_f.data[index].name)
                # print(self.curr_para)
                self.control_f.data.pop(index)
            elif f_name == "ack_query_f":
                self.curr_data.pop(self.ack_query_f.data[index].name)
                self.ack_query_f.data.pop(index)
            elif f_name == "ack_control_f":
                self.ack_control_f.data.pop(index)
            else:
                raise Exception(f"未定义帧{f_name}")
            return True, None
        except Exception as e:
            return False, e

    def connect(self) -> bool:
        self.reset_error()
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
        # self.logger.info(f"查询指令:{query_byte.hex()}")
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
        # self.logger.info(f"查询回复:{response.hex()}")

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
                self.logger.info(f"查询到故障! 故障码:{self.curr_data["故障"]}")
                self.run_state = False
                self.breakdown = True
        else:
            self.logger.error("error! 未查询到故障信息，请检查查询回复报文设置是否正确！")
        return True

    def read_msg(self) -> tuple[bytes, bool]:
        try:
            read_count = 0
            while self.ser.in_waiting < 4:
                read_count += 1
                time.sleep(0.005)
                if read_count == 100:
                    self.logger.error(f"读取串口数据超时,情况1！")
                    return b"", False
            recv = self.ser.read(4)
            read_count = 0
            while self.ser.in_waiting < recv[3] + 2:
                read_count += 1
                time.sleep(0.005)
                if read_count == 100:
                    self.logger.error(f"读取串口数据超时，情况2")
                    return b"", False
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
                "控制命令": "清障",
            }
            if self.write(para_dict):
                self.breakdown = False
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
                    self.query_f.load_framer(value)
                elif key == "control_f":
                    self.control_f.reset_all()
                    self.control_f.load_framer(value)
                    for _, value in self.control_f.data.items():
                        self.curr_para[value.name] = 0
                elif key == "ack_query_f":
                    self.ack_query_f.reset_all()
                    self.ack_query_f.load_framer(value)
                    for _, value in self.ack_query_f.data.items():
                        self.curr_data[value.name] = 0
                elif key == "ack_control_f":
                    self.ack_control_f.reset_all()
                    self.ack_control_f.load_framer(value)
                elif key == "hardware_para":
                    self.update_hardware_parameter(value)
            self.logger.info("风机帧配置导入成功！")
            return True, None
        except Exception as e:
            self.logger.error(f"风机帧配置导入error！{e}")
            return False, e

    def export_config(self):
        return {
            "query_f": self.pre_dict(self.query_f.export_framer()),
            "control_f": self.pre_dict(self.control_f.export_framer()),
            "ack_query_f": self.pre_dict(self.ack_query_f.export_framer()),
            "ack_control_f": self.pre_dict(self.ack_control_f.export_framer()),
            "hardware_para": self.get_hardware_parameter(),
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
        # 有无控制命令，若没有控制命令而且电机关着，那么默认为启动
        if self.command not in para_dict:
            if self.run_state == False:
                para_dict[self.command] = "启动"
            else:
                para_dict[self.command] = "write"

        if para_dict[self.command] == "start" or para_dict[self.command] == "启动":
            command_value = 1
            # 启动时的参数必须全
            for key in self.curr_para.keys():
                if key not in para_dict:
                    self.logger.error(f"参数不全！{key}")
                    return False
        elif para_dict[self.command] == "stop" or para_dict[self.command] == "停止":
            command_value = 2
        elif para_dict[self.command] == "clear_breakdown" or para_dict[self.command] == "清障":
            command_value = 4
        else:
            command_value = 0
            # 写的参数也必须全
            for key in self.curr_para.keys():
                if key not in para_dict:
                    self.logger.error(f"参数不全！{key}")
                    return False

        for key, value in para_dict.items():
            # print(key,value)
            if key == "控制命令":
                self.control_f.gen_data(key, command_value)
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
        if command_value == 1:
            self.run_state = True
            for key in self.curr_para:
                self.curr_para[key] = para_dict[key]
        elif command_value == 2:
            self.run_state = False
            for key in self.curr_para:
                self.curr_para[key] = 0
        elif command_value == 4:
            self.breakdown = False
            for key in self.curr_para:
                self.curr_para[key] = 0
        else:
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
        for key, value in para_dict.items():
            if key == "cpu":
                self.set_device_cpu(value)
            elif key == "port":
                self.set_port(value)
            elif key == "baudrate":
                self.set_baudrate(value)
            else:
                self.logger.error(f"未定义的参数{key}")
        return True

    def get_hardware_parameter(self) -> dict[str, any]:
        return {"cpu": self.cpu, "port": self.port, "baudrate": self.serial_baudrate}

    def close_device(self):
        return self.write({"控制命令": "停止"})


if __name__ == "__main__":
    fan_driver = FanDriver("Fan", device_address="01", cpu="M0", port=serial_port)
    # fan_driver.update_hardware_parameter({"device_address": "034", "cpu": "M0", "port": "COM6"})
    # print(fan_driver.get_hardware_parameter())
    fan_driver.updata_F_data(f_name="ack_query_f", index=1, name="修改1", type="bit8", size=1, formula="")
    print(fan_driver.curr_data)
    fan_driver.updata_F_data(f_name="control_f", index=2, name="修改2", type="bit16", size=2, formula="")
    print(fan_driver.curr_para)
    fan_driver.updata_F_data(f_name="control_f", index=2, name="修改3", type="int16", size=2, formula="")
    fan_driver.updata_F_data(f_name="control_f", index=2, name="修改2", type="float", size=2, formula="real_data=raw_data")
    print(fan_driver.curr_para)
    fan_driver.updata_F_data(f_name="control_f", index=2, name="修改4", type="int16", size=2, formula="real_data=raw_data*2")
    print(fan_driver.curr_para)
    # fan_driver.connect()
    # fan_driver.read_all()
    # print(fan_driver.ack_query_f.get_data())
    # fan_driver.control_f.set_data(index=6, name="new", type="int16", size=2, formula="real_data=raw_data*100")
    # json_dict = fan_driver.export_config()
    # print(json_dict)
    # fan_driver2 = FanDriver("Fan2", [], [], device_address="01", cpu="M0", port=serial_port)
    # fan_driver2.load_config(json_dict)
    # print(fan_driver2.export_config())

    # para_dict = {
    #     "控制命令": "start",
    #     "给定转速": 1,
    #     "速度环补偿带宽": 2,
    #     "电流环带宽": 3,
    #     "观测器补偿带宽": 4,
    # }
    # fan_driver.set_default()
    # fan_driver.write(para_dict)
