import time

from pymodbus.framer import ModbusSocketFramer

from .driver_base import DriverBase
from pymodbus.client import ModbusTcpClient
import struct
import ipaddress


class TestDevice(DriverBase):

    def __init__(self, device_name: str, data_list: list[str], para_list: list[str]):
        super().__init__(device_name, data_list, para_list)
        self.__set_client(ip="127.0.0.1", port=5020)
        self.hardware_para = ["ip", "port"]
        self.command = "test_device_command"

    def __set_client(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.client = ModbusTcpClient(host=ip, port=port)

    def write(self, para_dict: dict[str, any]) -> bool:
        """
        para_dict示例{"test_device_command":"command", "load":float}
        command:"start_device","stop_device","P_mode","N_mode","N1_mode","write"
        """
        # address = 0  # 读取寄存器的起始地址
        # count = 3  # 读取的数字
        # coding = 4  # 编码格式占字节数，如果是float为4
        # slave = 1  # 设置从机地址
        # result = self.client.read_holding_registers(address=address, count=count * coding, slave=slave,
        #                                             timeout=5)  # 请求应该为00 01 00 00 00 06 01 03 00 01 00 0C
        if not self.check_writable():
            self.logger.error(f"串口不可写!")
            return False
        self.__iswriting = True
        if not self.conn_state:
            self.logger.error(f"服务器未连接! 非法写！")
            self.__iswriting = False
            return False
        if self.command not in para_dict:
            command = "write"
        else:
            command = para_dict[self.command]
        if command == "start_device":
            address = 0
            value = 1
            result = self.client.write_register(address, value, slave=1)
        elif command == "stop_device":
            address = 0
            value = 0
            result = self.client.write_register(address, value, slave=1)
        elif command == "P_mode":
            address = 1
            value = 1
            result = self.client.write_register(address, value, slave=1)
        elif command == "N_mode":
            address = 1
            value = 2
            result = self.client.write_register(address, value, slave=1)
        elif command == "N1_mode":
            address = 1
            value = 4
            result = self.client.write_register(address, value, slave=1)
        elif command == "write":
            address = 2
            data_value = float(para_dict["load"])
            # 将浮点数打包为四个字节
            packed_value = struct.pack(">f", data_value)
            # 将四个字节解包为两个16位的整数
            registers = struct.unpack(">HH", packed_value)
            # 将两个整数写入到两个连续的寄存器中
            value = list(registers)
            result = self.client.write_registers(address, value, slave=1)
        else:
            self.logger.error(f"发送指令错误：{command}")
            self.__iswriting = False
            return False
        self.logger.info(f"发送指令：{command, value}")
        if result.isError():
            self.logger.error(f"发送失败！")
            self.__iswriting = False
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
            self.__iswriting = False
            return True

    def connect(self) -> bool:
        try:
            self.conn_state = self.client.connect()
            self.logger.info(f"client连接到服务器{self.client}")
            return True
        except Exception as e:
            self.logger.error(f"连接错误！ error:{e}")
            return False

    def disconnect(self) -> bool:
        try:
            self.client.close()
            self.conn_state = False
            self.logger.info(f"连接关闭！")
            return True
        except Exception as e:
            self.logger.error(f"连接关闭错误！error:{e}")
            return False

    def recv_one(self, timeout: float = 1):
        self.client.comm_params.timeout_connect = timeout  # 设置接收超时时间，如果超时即使接收的字节数少于目标值也返回
        try:
            msg = self.client.recv(6)
            if len(msg) == 6:  # 数据头
                length = int.from_bytes(msg[-2:], byteorder="big", signed=False)
                msg += self.client.recv(length)
                if len(msg) == 6 + length:
                    self.logger.info(f"收到的报文为：{msg.hex()}")
                    return msg
                else:
                    raise Exception(f"接收到的数据长度不符合预期:{msg.hex()}")
            else:
                raise Exception(f"接收到的数据头长度不符合预期:{msg.hex()}")
        except Exception as e:
            self.logger.error(f"接收错误! error:{e}")
            return
        finally:
            pass  # 收尾

    def recv(self, timeout=0.05):
        msg = self.recv_one(timeout * 10)  # 放大区间使得可以收到报文
        count = 0
        while msg:  # 如果报文不为空，则可能后面有新报文
            count += 1
            msg_cache = self.recv_one(timeout)  # 更新新报文
            if msg_cache and count < 20:
                msg = msg_cache
            else:
                if count == 20:
                    self.logger.warn(f"警告更新报文时间设置过长！ 报文更新周期小于{timeout}s")
                elif count == 0:
                    self.logger.warn(f"警告更新报文时间设置过短！请增大！ 报文更新周期大于{timeout*10}s")
                break
        return msg

    def read_all(self, num=3, read_count=3, encoding=4) -> bool:
        for count in range(read_count):
            try:
                result = self.recv()
                if not result:
                    raise Exception(f"接收失败! result：{result.hex()}")
                else:
                    tid, pid, length, uid, fc, data_size = struct.unpack(">HHHBBB", result[:9])
                    if data_size == num * encoding:
                        float_values = [struct.unpack(">f", result[i : i + 4])[0] for i in range(9, 9 + num * encoding, encoding)]
                        self.logger.info(
                            f"tid, pid, length, uid：{tid, pid, length, uid},Function Code:{fc},data_size:{data_size},数据：{float_values}"
                        )
                        self.curr_data["motor_input_power"] = float_values[0]
                        self.curr_data["torque"] = float_values[1]
                        self.curr_data["motor_output_power"] = float_values[2]
                        return True
                    else:
                        raise Exception(f"数据接收数量错误！ 目标接收num*encoding：{num * encoding},实际收到：{data_size}")
            except Exception as e:
                self.logger.error(f"error:{e},count：{count}")
        return False

    def handle_breakdown(self, breakdown: int) -> bool:
        try:
            if breakdown != 0:
                parameters = {"test_device_command": "P_mode"}
                if not testdevice.write(parameters):
                    raise Exception(f"{parameters}")
                parameters = {"test_device_command": "write", "load": float(0) / 10}  # 假设空载为0
                if not testdevice.write(parameters):
                    raise Exception(f"{parameters}")
                parameters = {"test_device_command": "start_device"}
                if not testdevice.write(parameters):
                    raise Exception(f"{parameters}")
            else:
                self.logger.error(f"未收到故障码！")
            return True
        except Exception as e:
            self.logger.error(f"故障处理模块报错！ error:{e}")
            self.logger.error(f"再次尝试空载！")
            parameters = {"test_device_command": "P_mode"}
            testdevice.write(parameters)
            parameters = {"test_device_command": "write", "load": float(0) / 10}  # 假设空载为0
            testdevice.write(parameters)
            parameters = {"test_device_command": "start_device"}
            testdevice.write(parameters)
        finally:
            return False

    def update_hardware_parameter(self, para_dict: dict[str, any]) -> bool:
        selfip = self.ip
        selfport = self.port
        for key, value in para_dict.items():
            if key == "ip":
                try:
                    ipaddress.ip_address(value)
                    selfip = value
                except ValueError:
                    return False
            elif key == "port":
                if type(value) == int:
                    selfport = value
                else:
                    # raise TypeError("port must be an integer.")
                    return False
            else:
                raise KeyError(f"{key} is not a valid parameter.")
        self.__set_client(selfip, selfport)
        return True

    def get_hardware_parameter(self) -> dict[str, any]:
        return {"ip": self.ip, "port": self.port}


if __name__ == "__main__":
    testdevice = TestDevice(
        device_name="TestDevice", data_list=["motor_input_power", "torque", "motor_output_power"], para_list=["test_device_command", "load"]
    )
    # testdevice.update_hardware_parameter(para_dict={"ip": "127.0.0.1", "port": 504})
    # print(testdevice.connect())
    # testdevice.update_hardware_parameter(para_dict={"ip": "120.76.28.211", "port": 80})
    # parameters = {"test_device_command": "start_device"}
    # testdevice.write(parameters)
    # parameters = {"test_device_command": "write", "load": 200}
    while 1:
        testdevice.read_all()
        # testdevice.write(parameters)
        time.sleep(0.1)
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
