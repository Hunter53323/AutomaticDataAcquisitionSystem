from .driver_base import DriverBase
from pymodbus.client import ModbusTcpClient
import struct
import ipaddress


class TestDevice(DriverBase):

    def __init__(self, device_name: str, data_list: list[str], para_list: list[str]):
        super().__init__(device_name, data_list, para_list)
        self.ip = "127.0.0.1"
        self.port = 503
        self.client = ModbusTcpClient(self.ip, self.port)
        self.hardware_para = ["ip", "port"]

    def __set_client(self, ip: str, port: int):
        try:
            ipaddress.ip_address(ip)
            self.ip = ip
            self.port = port
            self.client = ModbusTcpClient(ip, port)
            return True
        except ValueError:
            return False
        except Exception as e:
            return False

    def write(self, para_dict: dict[str, any]) -> bool:
        """
        para_dict示例{"test_device_command":"start_device", "load":float}
        command:"start_device","stop_device","P_mode","N_mode","N1_mode","write"
        """
        if not self.conn_state:
            return False
        if "test_device_command" not in para_dict:
            command = "write"
        else:
            command = para_dict["test_device_command"]
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
            data_value = float(para_dict["load"])

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
            # 确认写正确后，更改状态值
            if command == "start_device":
                self.run_state = True
            elif command == "stop_device":
                self.run_state = False
            for key in self.curr_para:
                if key in para_dict:
                    self.curr_para[key] = para_dict[key]
            return True

    def connect(self) -> bool:
        try:
            self.conn_state = self.client.connect()
            return self.conn_state
        except:
            print("连接失败")
            return False

    def disconnect(self) -> bool:
        try:
            self.client.close()
            self.conn_state = False
            return True
        except:
            return False

    def read_all(self) -> bool:
        address = 1
        count = 12

        result = self.client.read_holding_registers(address, count, unit=1)
        if not result.isError():
            registers = result.registers
            packed_values = [registers[i : i + 2] for i in range(0, len(registers), 2)]
            float_values = [struct.unpack(">f", struct.pack(">HH", *pack))[0] for pack in packed_values]

            self.curr_data["motor_input_power"] = float_values[0]
            self.curr_data["torque"] = float_values[1]
            self.curr_data["motor_output_power"] = float_values[2]

    def update_hardware_parameter(self, para_dict: dict[str, any]) -> bool:
        selfip = self.ip
        selfport = self.port
        for key, value in para_dict.items():
            if key == "ip":
                selfip = value
            elif key == "port":
                if type(value) == int:
                    selfport = value
                else:
                    # raise TypeError("port must be an integer.")
                    return False
            else:
                raise KeyError(f"{key} is not a valid parameter.")
        return self.__set_client(selfip, selfport)


if __name__ == "__main__":
    testdevice = TestDevice(
        device_name="test_device",
        data_list=["input_power", "torque", "output_power"],
        para_list=["command", "load"],
    )

    testdevice.update_hardware_parameter(para_dict={"ip": "127.0.0.1", "port": 504})
    print(testdevice.connect())
    testdevice.update_hardware_parameter(para_dict={"ip": "127.0.0.1", "port": 503})
    print(testdevice.connect())

    # testdevice.read_all()
    # print("Test read:", testdevice.curr_data)
    # parameters = {"command": "start_device"}
    # print("Test start:", testdevice.write(parameters))
    # parameters = {"command": "stop_device"}
    # print("Test stop:", testdevice.write(parameters))
    # parameters = {"command": "P_mode"}
    # print("Test P:", testdevice.write(parameters))
    # parameters = {"command": "N_mode"}
    # print("Test N:", testdevice.write(parameters))
    # parameters = {"command": "N1_mode"}
    # print("Test N1:", testdevice.write(parameters))
    # parameters = {"command": "write", "loading": 200}
    # print("Test write:", testdevice.write(parameters))
    # testdevice.disconnect()
