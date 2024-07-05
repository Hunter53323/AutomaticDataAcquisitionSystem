from .driver_base import DriverBase
from pymodbus.client import ModbusTcpClient
import struct


class TestDevice(DriverBase):

    def __init__(self, device_name: str, data_list: list[str], para_list: list[str]):
        super().__init__(device_name, data_list, para_list)
        self.client = ModbusTcpClient("127.0.0.1", 503)

    def write(self, para_dict: dict[str, any]) -> bool:
        """
        para_dict示例{"command":"start_device", "loading":float}
        command:"start_device","stop_device","P_mode","N_mode","N1_mode","write"
        """
        command = para_dict["command"]
        if not self.conn_state:
            return False
        if command == "start_device":
            address = 0
            value = 1
            result = self.client.write_register(address, value, unit=1)
        elif command == "stop_device":
            address = 0
            value = 0
            result = self.client.write_register(address, value, unit=1)
        elif command == "P_mode":
            address = 1
            value = 1
            result = self.client.write_register(address, value, unit=1)
        elif command == "N_mode":
            address = 1
            value = 2
            result = self.client.write_register(address, value, unit=1)
        elif command == "N1_mode":
            address = 1
            value = 4
            result = self.client.write_register(address, value, unit=1)
        elif command == "write":
            address = 2
            data_value = float(para_dict["loading"])

            # 将浮点数打包为四个字节
            packed_value = struct.pack(">f", data_value)
            # 将四个字节解包为两个16位的整数
            registers = struct.unpack(">HH", packed_value)
            # 将两个整数写入到两个连续的寄存器中
            value = list(registers)
            result = self.client.write_registers(address, value, unit=1)
        else:
            return False

        if result.isError():
            return False
        else:
            return True

    def connect(self) -> bool:
        self.conn_state = self.client.connect()
        return self.conn_state

    def disconnect(self) -> bool:
        self.client.close()
        self.conn_state = False

    def read_all(self) -> bool:
        address = 1
        count = 12

        result = self.client.read_holding_registers(address, count, unit=1)
        if not result.isError():
            registers = result.registers
            packed_values = [registers[i : i + 2] for i in range(0, len(registers), 2)]
            float_values = [struct.unpack(">f", struct.pack(">HH", *pack))[0] for pack in packed_values]

            self.curr_data["input_power"] = float_values[0]
            self.curr_data["torque"] = float_values[1]
            self.curr_data["output_power"] = float_values[2]


if __name__ == "__main__":
    testdevice = TestDevice(
        device_name="test_device",
        data_list=["input_power", "torque", "output_power"],
        para_list=["command", "loading"],
    )
    testdevice.connect()
    testdevice.read_all()
    print("Test read:", testdevice.curr_data)
    parameters = {"command": "start_device"}
    print("Test start:", testdevice.write(parameters))
    parameters = {"command": "stop_device"}
    print("Test stop:", testdevice.write(parameters))
    parameters = {"command": "P_mode"}
    print("Test P:", testdevice.write(parameters))
    parameters = {"command": "N_mode"}
    print("Test N:", testdevice.write(parameters))
    parameters = {"command": "N1_mode"}
    print("Test N1:", testdevice.write(parameters))
    parameters = {"command": "write", "loading": 200}
    print("Test write:", testdevice.write(parameters))
    testdevice.disconnect()
