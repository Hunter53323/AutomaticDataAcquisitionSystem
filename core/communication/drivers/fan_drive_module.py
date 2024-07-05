import serial
from .driver_base import DriverBase
import time

serial_port = "COM10"  # 请替换为您的串行端口
serial_baudrate = 9600  # 根据实际情况设置波特率
serial_parity = "N"  # None表示无校验
serial_stopbits = 1  # 停止位
serial_bytesize = 8  # 数据位


class FanDriver(DriverBase):
    def __init__(self, device_name: str, data_list: list[str], para_list: list[str], **kwargs):
        super().__init__(device_name, data_list, para_list)
        self.device_address = None
        for key, value in kwargs.items:
            if key == "device_address":
                self.device_address = value

        self.ser: serial.Serial = serial.Serial(
            port=serial_port, baudrate=serial_baudrate, parity=serial_parity, stopbits=serial_stopbits, bytesize=serial_bytesize, timeout=10
        )

    def connect(self) -> bool:
        self.ser.open()
        if self.ser.is_open:
            return True
        else:
            return False

    def disconnect(self) -> bool:
        self.ser.close()
        if self.ser.is_open:
            return False
        else:
            return True

    def read(self, data_name_list: list[str] = None) -> dict[str, any]:
        data0 = "A5"
        data1 = self.device_address
        data2 = "02"
        data3 = "00"
        byte0to3 = bytes.fromhex(data0 + data1 + data2 + data3)
        byte4 = self.__calculate_checksum(byte0to3)
        byte5 = b"\x5A"

        byte_data = byte0to3 + byte4 + byte5
        self.ser.write(byte_data)
        response_size = 4  # 假设响应是4个字节
        response = self.ser.read(response_size)

        # 将字节转换为十六进制字符串
        hex_response = response.hex()
        print(f"Response (hex): {hex_response}")

    def write(self, para_dict: dict[str, Any]) -> bool:
        return super().write(para_dict)

    def __calculate_checksum(data: bytes) -> bytes:
        # 初始化校验和为0
        checksum = 0
        print(data)

        # 对数据中的每个字节进行累加
        for byte in data:
            checksum += byte
        print(checksum)

        # 取累加结果的低8位
        checksum_low8 = checksum & 0xFF

        return bytes([checksum_low8])
