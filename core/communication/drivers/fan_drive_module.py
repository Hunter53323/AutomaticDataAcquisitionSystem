import serial
from serial.serialutil import SerialTimeoutException
from .driver_base import DriverBase
import time
from typing import Union

serial_port = "COM9"  # 请替换为您的串行端口
serial_baudrate = 9600  # 根据实际情况设置波特率
serial_parity = "N"  # None表示无校验
serial_stopbits = 1  # 停止位
serial_bytesize = 8  # 数据位


class FanDriver(DriverBase):
    def __init__(self, device_name: str, data_list: list[str], para_list: list[str], **kwargs):
        super().__init__(device_name, data_list, para_list)
        self.device_address = None
        self.cpu = None
        for key, value in kwargs.items():
            if key == "device_address":
                self.set_device_address(value)
            if key == "cpu":
                if value != "M0" and value != "M4":
                    raise ValueError("Invalid cpu value")
                self.cpu = value

        self.ser: serial.Serial = serial.Serial(
            port=serial_port, baudrate=serial_baudrate, parity=serial_parity, stopbits=serial_stopbits, bytesize=serial_bytesize, timeout=10
        )

    def set_device_address(self, device_address: bytes) -> bool:
        self.device_address = f"{device_address[0]:02x}"
        return True

    def set_device_cpu(self, cpu: str) -> bool:
        self.cpu = cpu
        return True

    def connect(self) -> bool:
        if (self.device_address is None) or (self.cpu is None):
            return False
        if self.ser.is_open:
            return True
        self.ser.open()
        if self.ser.is_open:
            self.conn_state = True
            return True
        else:
            return False

    def disconnect(self) -> bool:
        self.ser.close()
        if self.ser.is_open:
            return False
        else:
            self.conn_state = False
            return True

    def __serwrite(self, byte_data: bytes, count: int = 0) -> tuple[bool, str]:
        """
        自定义的写操作，最多尝试重写三次
        """
        try:
            self.ser.write(byte_data)
            return True, ""
        except SerialTimeoutException as e:
            print(e)
            return False, "Timeout"
        except Exception as e:
            if count == 3:
                print(e)
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
        # self.ser.write(byte_data)
        # 写以及写出错的处理
        write_status, err = self.__serwrite(byte_data)
        if not write_status:
            return False

        response = self.ser.read_until(b"\xA5")
        # 检测收到的数据是否是预期的数据，否则报错
        if len(response) != 18:
            if read_count == 3:
                return False
            return self.read_all(read_count=read_count + 1)
        # 检查校验和是否相符
        response_checksum = self.__calculate_checksum(response[0:16])
        if response[16].to_bytes() != response_checksum:
            if read_count == 3:
                return False
            return self.read_all(read_count=read_count + 1)
        # 数据检查完毕后开始读取数据
        target_speed, actual_speed, dc_bus_voltage, U_phase_current, power, breakdown = self.__decode_read_response(response)
        self.curr_data = {
            "target_speed": target_speed,
            "actual_speed": actual_speed,
            "dc_bus_voltage": dc_bus_voltage,
            "U_phase_current": U_phase_current,
            "power": power,
            "breakdown": breakdown,
        }
        return True

    def write(self, para_dict: dict[str, any], write_count: int = 1) -> bool:
        """
        控制指令
        """
        data0 = "A5"
        data1 = self.device_address
        data2 = "01"
        data3 = "03"
        if para_dict["fan_command"] == "start":
            data4 = "01"
        elif para_dict["fan_command"] == "stop":
            data4 = "02"
        elif para_dict["fan_command"] == "clear_breakdown":
            data4 = "04"
        else:
            data4 = "00"
        byte0to4 = bytes.fromhex(data0 + data1 + data2 + data3 + data4)
        # 第五和第六个字节是转速
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

        # self.ser.write(write_bytes)
        # 写以及写出错的处理
        write_status, err = self.__serwrite(write_bytes)
        if not write_status:
            return False

        response = self.ser.read_until(b"\xA5")
        # 检测收到的数据是否是预期的数据，否则报错
        if len(response) != 7:
            if write_count == 3:
                return False
            return self.write(para_dict, write_count=write_count + 1)

        # 根据校验和和校验结果判断是否成功
        response_checksum = self.__calculate_checksum(response[0:5])
        # 取出的单个字节是int类型，response_checksum是bytes类型，需要转换
        if response[5].to_bytes() == response_checksum:
            if response[4].to_bytes() == b"\x01":
                return True
            else:
                if write_count == 3:
                    return False
                return self.write(para_dict, write_count=write_count + 1)
        else:
            return False

    def __decode_read_response(self, response: bytes) -> tuple[int, int, int, int, int, list, bool]:
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
            if (response[15] & (1 << i)) != 0:
                breakdown.append(i + 8)
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
            if key not in ["device_address", "cpu"]:
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
            else:
                # raise ValueError("Unknown parameter")
                return False
        for key, value in para_dict.items():
            if key == "device_address":
                self.set_device_address(value)
            elif key == "cpu":
                self.set_device_cpu(value)
            else:
                return False
        return True


if __name__ == "__main__":
    fan_driver = FanDriver("Fan", ["speed", "temperature"], ["speed", "temperature"], device_address="01", cpu="M0")
