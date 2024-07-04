from pymodbus.client import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import ConnectionException
import time
from core.communication.drivers.ParametersConfig import DEVICES


class ReadWriteError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class Driver:
    def __init__(self, device_tuple_list: list):
        """
        输入设备元组列表进行初始化
        example: Driver([("device1", "COM1"), ("device2", "COM2")])
        """
        self.clientdict = {}
        for atuple in device_tuple_list:
            if type(atuple) != tuple or len(atuple) != 2:
                raise Exception("设备元组格式错误")
            if atuple[0] in DEVICES.keys():
                self.add_device(atuple[0], atuple[1])
            else:
                raise Exception("设备不在配置文件中")

    def add_device(self, device_name: str, port: str):
        """
        添加设备
        """
        if self.clientdict.get(device_name) is not None:
            print("设备已存在,将会更新端口")

        self.clientdict[device_name] = ModbusClient(method="rtu", port=port, stopbits=1, bytesize=8, parity="N", baudrate=9600)

    def delete_device(self, device_name: str):
        """
        删除设备
        """
        if self.clientdict.get(device_name) is None:
            print("设备不存在")
            return

        self.clientdict.pop(device_name)

    def get_device_name(self):
        """
        获取设备名称
        """
        return list(self.clientdict.keys())

    def connect_device(self, device_name: str) -> bool:
        """
        连接设备,并返回连接状态
        """
        if self.clientdict.get(device_name) is None:
            print("设备不存在,请添加设备")
            return False

        device: ModbusClient = self.clientdict[device_name]
        testread = device.read_holding_registers(address=0, count=1, unit=1)
        if testread.isError():
            return False
        return device.connect()

    def connect_all_device(self):
        """
        连接所有设备,并返回连接状态
        """
        for device_name in self.clientdict.keys():
            connection = self.connect_device(device_name)
            if not connection:
                print("设备" + device_name + "连接失败")
                return False
        return True

    def read(self, device_name: str, address) -> tuple[bool, list]:
        try:
            if self.clientdict.get(device_name) is None:
                raise Exception("设备不存在")
            device: ModbusClient = self.clientdict[device_name]
            re = device.read_holding_registers(address=address, count=1, unit=1)
            if re.isError():
                re = device.read_holding_registers(address=address, count=1, unit=1)
                if re.isError():
                    raise ReadWriteError("读取失败")
            return not re.isError(), re.registers
        except ConnectionException as ce:
            print(ce)
        except ReadWriteError as rwe:
            print(rwe)
        except Exception as e:
            print(e)

    def read_from_parameter(self, device_name: str, parameter_name: str):
        if device_name in DEVICES.keys():
            if parameter_name in DEVICES[device_name].keys():
                return self.read(device_name=device_name, address=DEVICES[device_name][parameter_name])
            else:
                raise ValueError("参数不存在")
        else:
            raise ValueError("设备不存在")

    def write_from_parameter(self, device_name: str, parameter_name: str, value):
        if device_name in DEVICES.keys():
            if parameter_name in DEVICES[device_name].keys():
                return self.write(device_name=device_name, address=DEVICES[device_name][parameter_name], value=value)
            else:
                raise ValueError("参数不存在")
        else:
            raise ValueError("设备不存在")

    def write(self, device_name: str, address, value) -> bool:
        try:
            if self.clientdict.get(device_name) is None:
                raise Exception("设备不存在")
            device: ModbusClient = self.clientdict[device_name]
            re = device.write_register(address=address, value=value, unit=1)
            if re.isError():
                re = device.write_register(address=address, value=value, unit=1)
                if re.isError():
                    raise ReadWriteError("写入失败")
            return not re.isError()
        except ConnectionException as ce:
            print(ce)
        except ReadWriteError as rwe:
            print(rwe)
        except Exception as e:
            print(e)

    def close(self):
        for device_name in self.clientdict.keys():
            self.clientdict[device_name].close()


if __name__ == "__main__":
    import time

    client = Driver([("电机驱动", "COM8")])
    client.connect_all_device()
    # print(client.write(device_name="test", address=0, value=1234))
    # print(client.read(device_name="test", address=0))
    # print(client.write_from_parameter("电机驱动", "实际转速", 1234))
    start = time.time()
    # client.read_from_parameter("电机驱动", "实际转速")
    client.read("电机驱动", 0)
    print(time.time() - start)
    client.close()
    # client.read("test", address=0)

    # try:
    #     # 连接到服务器
    #     connection = client.connect()
    #     if connection:
    #         print("Connected to Modbus RTU Server")

    #         # 读取保持寄存器
    #         rr = client.read_holding_registers(address=0, count=1, unit=1)
    #         print("Read Result: ", rr.registers)

    #         # 写入单个寄存器
    #         rq = client.write_register(address=0, value=1234, unit=1)
    #         print("Write Result: ", rq)

    #         # 再次读取保持寄存器以验证写入
    #         rr = client.read_holding_registers(address=0, count=1, unit=1)
    #         print("Read Result after write: ", rr.registers)
    #     else:
    #         print("Failed to connect to Modbus RTU Server")

    # except ConnectionException as ce:
    #     print("Connection failed: ", ce)

    # finally:
    #     # 关闭连接
    #     client.close()
