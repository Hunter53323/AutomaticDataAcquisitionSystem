from typing import Tuple, List

import serial
from serial.serialutil import SerialTimeoutException
from .driver_base import DriverBase
import time
import copy

serial_port = "COM9"  # 请替换为您的串行端口
serial_baudrate = 9600  # 根据实际情况设置波特率
serial_parity = "N"  # None表示无校验
serial_stopbits = 1  # 停止位
serial_bytesize = 8  # 数据位

breakdownmap = {0: "采样偏置故障", 1: "缺相故障", 2: "硬件过流故障", 3: "电机堵转故障", 4: "电机失步故障",
                5: "软件 RMS 过流故障", 6: "软件峰值过流故障", 7: "直流母线欠压故障", 8: "IPM 过温故障",
                9: "启动失败故障", 10: "直流母线过压故障", 11: "网压瞬时掉电故障"}


class FanDriver(DriverBase):
    def __init__(self, device_name: str, data_list: list[str], para_list: list[str], **kwargs):
        super().__init__(device_name, data_list, para_list)
        # 协议要求，未赋值的参数为0
        for key in self.curr_para:
            self.curr_para[key] = 0
        self.device_address = None
        self.cpu = None
        self.port = None
        for key, value in kwargs.items():
            if key == "device_address":
                self.set_device_address(value)
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
        self.hardware_para = ["device_address", "cpu"]
        self.command = "fan_command"

        self.ser: serial.Serial = serial.Serial(
            baudrate=serial_baudrate, parity=serial_parity, stopbits=serial_stopbits,
            bytesize=serial_bytesize, timeout=10
        )

    def set_device_address(self, device_address: bytes) -> bool:
        self.device_address = f"{device_address[0]:02x}"
        return True

    def set_device_cpu(self, cpu: str) -> bool:
        self.cpu = cpu
        return True

    def connect(self) -> bool:
        if self.device_address is None:
            self.logger.error("device_address is None")
            return False
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
        data0 = "A5"
        data1 = self.device_address
        data2 = "02"
        data3 = "00"
        byte0to3 = bytes.fromhex(data0 + data1 + data2 + data3)
        byte4 = self.__calculate_checksum(byte0to3)
        byte5 = b"\x5A"

        byte_data = byte0to3 + byte4 + byte5
        self.logger.debug(f"查询指令:{byte_data.hex()}")
        # self.ser.write(byte_data)
        # 写以及写出错的处理
        write_status, err = self.__serwrite(byte_data)
        if not write_status:
            self.logger.error(f"查询指令写入串口报错! reason:{err},查询指令:{byte_data.hex()}")
            return False

        response = self.read_msg()
        self.logger.debug(f"查询回复:{response.hex()}")
        # response = self.ser.read_until(b"\xA5")
        # 检测收到的数据是否是预期的数据，否则报错
        if len(response) != 18:
            # print("count",read_count)
            self.logger.error(
                f"查询回复报错! len(response) != 18?:{len(response) != 18},查询回复:{response.hex()},count:{read_count}")
            if read_count == 3:
                return False
            return self.read_all(read_count=read_count + 1)
        
        if response[17].to_bytes() != b"\xA5":
            self.logger.error(
                f"查询回复报错! response[17].to_bytes()!=\xA5?:{response[17].to_bytes() != b"\xA5"},查询回复:{response.hex()},count:{read_count}")
            if read_count == 3:
                return False
            return self.read_all(read_count=read_count + 1)

        # 检查校验和是否相符
        response_checksum = self.__calculate_checksum(response[0:16])
        if response[16].to_bytes() != response_checksum:
            self.logger.error(
                f"查询校验和报错! recv:{response[16].to_bytes()},cal:{response_checksum},count:{read_count}")
            if read_count == 3:
                return False
            return self.read_all(read_count=read_count + 1)
        # 数据检查完毕后开始读取数据
        target_speed, actual_speed, dc_bus_voltage, U_phase_current, power, breakdowns = self.__decode_read_response(
            response)
        self.curr_data = {
            "target_speed": target_speed,
            "actual_speed": actual_speed,
            "dc_bus_voltage": dc_bus_voltage,
            "U_phase_current": U_phase_current,
            "power": power,
            "breakdown": breakdowns,
        }
        if len(breakdowns) > 0:
            self.logger.info(f"查询到故障! 故障码:{', '.join(str(breakdown) for breakdown in breakdowns)}")
            self.run_state = False
            self.breakdown = True
        return True

    def read_msg(self):
        while self.ser.in_waiting < 4:
            time.sleep(0.01)
        recv = self.ser.read(4)
        while self.ser.in_waiting < recv[3] + 2:
            time.sleep(0.01)
        recv = recv + self.ser.read(recv[3] + 2)
        return recv

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

    def write(self, para_dict: dict[str, any], write_count: int = 1) -> bool:
        """
        控制指令
        """
        if not self.check_writable():
            self.logger.error(f"串口不可写!")
            return False
        self.__iswriting = True
        # 有无控制命令
        if self.command in para_dict:
            command = para_dict[self.command]
        else:
            command = "write"
        # 参数不全的情况下，需要将以往的参数补充上
        if write_count == 1:
            para_dict.update({key: self.curr_para[key] for key in self.curr_para if key not in para_dict})
        data0 = "A5"
        data1 = self.device_address
        data2 = "01"
        data3 = "09"  # 手册是03，但是实际传了9个字节
        if command == "start":
            data4 = "01"
        elif command == "stop":
            data4 = "02"
        elif command == "clear_breakdown":
            data4 = "04"
        else:
            data4 = "00"
        byte0to4 = bytes.fromhex(data0 + data1 + data2 + data3 + data4)
        # 第五和第六个字节是转速，卡范围
        speed: int = para_dict["set_speed"]
        byte5and6 = speed.to_bytes(2, byteorder="big", signed=False)
        # 第七个和第八个字节是速度环补偿带宽
        speed_loop_compensates_bandwidth: int = para_dict["speed_loop_compensates_bandwidth"]
        byte7and8 = (speed_loop_compensates_bandwidth * 10).to_bytes(2)
        # 第九个第十个字节是电流环带宽
        current_loop_compensates_bandwidth: int = para_dict["current_loop_compensates_bandwidth"]
        byte9and10 = current_loop_compensates_bandwidth.to_bytes(2)
        # 第十一个第十二个字节是观测器补偿带宽
        observer_compensates_bandwidth: int = para_dict["observer_compensates_bandwidth"]
        byte11and12 = (observer_compensates_bandwidth * 100).to_bytes(2)
        # 计算校验和
        bytes_data = byte5and6 + byte7and8 + byte9and10 + byte11and12
        checksum = self.__calculate_checksum(byte0to4, bytes_data)
        frame_end = b"\x5A"

        write_bytes = byte0to4 + bytes_data + checksum + frame_end
        self.logger.info(f"控制指令:{write_bytes.hex()}")
        # self.ser.write(write_bytes)
        # 写以及写出错的处理
        write_status, err = self.__serwrite(write_bytes)
        if not write_status:
            self.logger.error(f"控制指令写入串口报错！ 控制指令:{write_bytes.hex()},count:{write_count}")
            self.__iswriting = False
            return False

        response = self.ser.read_until(b"\xA5")
        self.logger.info(f"控制指令回复:{response.hex()}")
        # 检测收到的数据是否是预期的数据，否则报错
        if len(response) != 7:
            self.logger.error(
                f"控制回复报错! len(response) != 7?:{len(response) != 7},控制回复:{response.hex()},count:{write_count}")
            if write_count == 3:
                self.__iswriting = False
                return False
            return self.write(para_dict, write_count=write_count + 1)

        # 根据校验和和校验结果判断是否成功
        response_checksum = self.__calculate_checksum(response[0:5])
        # 取出的单个字节是int类型，response_checksum是bytes类型，需要转换
        if response[5].to_bytes() == response_checksum:
            if response[4].to_bytes() == b"\x01":
                # 确认读写操作正确后，修改参数表
                if command == "start":
                    self.run_state = True
                elif command == "stop":
                    self.run_state = False
                elif command == "clear_breakdown":
                    self.breakdown = False
                for key in self.curr_para:
                    self.curr_para[key] = para_dict[key]
                self.__iswriting = False
                return True
            else:
                self.logger.error(
                    f"控制回复校验结果报错! recv:{response[4].to_bytes()},shoulder:\x01,count:{write_count}")
                if write_count == 3:
                    self.__iswriting = False
                    return False
                return self.write(para_dict, write_count=write_count + 1)
        else:
            self.logger.error(
                f"控制回复校验和报错! recv:{response[5].to_bytes()},cal:{response_checksum},count:{write_count}")
            self.__iswriting = False
            return False

    def __decode_read_response(self, response: bytes) -> tuple[float, float, float, float, float, list[int]]:
        FB, VB, IB, Cofe1, Cofe2, Cofe3, Cofe4, Cofe5 = self.__get_cpu_paras()
        # 第四个和第五个字节是目标转速的高8位和低8位,两种方案都可以
        # target_speed = (response[4] << 8) | response[5]
        # 默认是大端序，无符号
        target_speed = int.from_bytes(response[4:6], byteorder="big", signed=False) * FB * Cofe1 / Cofe2
        # 第六个和第七个字节是实际转速的高8位和低8位
        actual_speed = int.from_bytes(response[6:8]) * FB * Cofe1 / Cofe2
        # 第八个和第九个字节是直流母线电压的高8位和低8位
        dc_bus_voltage = int.from_bytes(response[8:10]) * VB / Cofe2
        # 第十个和第十一个字节是U相电流的高8位和低8位
        U_phase_current = int.from_bytes(response[10:12]) * IB / Cofe2 / Cofe5
        # 第十二个和第十三个字节是功率的高8位和低8位
        power = int.from_bytes(response[12:14]) * IB * VB * Cofe3 / Cofe4 / Cofe2 / Cofe5
        # 第14个字节的每一个位都表示一种故障，8个位表示8种故障，用不同的字符串表示
        # 按照协议上从上到下的顺序从0开始罗列故障码
        breakdown = []
        for i in range(8):
            if (response[14] & (1 << i)) != 0:
                breakdown.append(i)
        for i in range(4):
            if (response[15] & (1 << i)) != 0:
                breakdown.append(i+8)
        # 第16个字节是校验和低8位，检查校验和,前面已经检查过了，因此此处不用再次检查
        # if self.__calculate_checksum(response[0:16]) == response[16].to_bytes():
        return target_speed, actual_speed, dc_bus_voltage, U_phase_current, power, breakdown

    def __get_cpu_paras(self) -> tuple[int, int, int, int, int, int, int, int]:
        if self.cpu == "M0":
            return 25, 380, 2, 60, 32768, 3, 2, 1
        elif self.cpu == "M4":
            return 1, 1, 1, 1, 1, 1, 1, 1000

    def __calculate_checksum(self, *args: bytes) -> bytes:
        # 初始化校验和为0
        checksum = 0

        # 对数据中的每个字节进行累加
        for data in args:
            for byte in data:
                checksum += byte

        # 取累加结果的低8位
        checksum_low8 = checksum & 0xFF

        return bytes([checksum_low8])

    def update_hardware_parameter(self, para_dict: dict[str, any]) -> bool:
        for key in para_dict.keys():
            if key not in ["device_address", "cpu", "port"]:
                # raise ValueError("Unknown parameter")
                return False
        for key, value in para_dict.items():
            if key == "device_address":
                if type(value) != bytes:
                    # raise ValueError("device_address must be bytes")
                    return False
                if len(value) != 1:
                    # raise ValueError("device_address must be 1 byte")
                    return False
            elif key == "cpu":
                if value not in ["M0", "M4"]:
                    # raise ValueError("cpu must be M0 or M4")
                    return False
            elif key == "port":
                if not isinstance(value, str):
                    # raise ValueError("port must be str")
                    return False
            else:
                # raise ValueError("Unknown parameter")
                return False
        for key, value in para_dict.items():
            if key == "device_address":
                self.set_device_address(value)
            elif key == "cpu":
                self.set_device_cpu(value)
            elif key == "port":
                self.port = value
            else:
                return False
        return True
    
    def get_hardware_parameter(self) -> dict[str, any]:
        return {"device_address": self.device_address, "cpu": self.cpu, "port": self.port}


if __name__ == "__main__":
    fan_driver = FanDriver("Fan", ["speed", "temperature"], ["speed", "temperature"], device_address=b"\x01", cpu="M0")
    fan_driver.read_all()
    # fan_driver.connect()
