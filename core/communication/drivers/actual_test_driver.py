import json
import time

from pymodbus.framer import ModbusSocketFramer
from .frame import modbus_frame
from .frame.modbus_frame import Field
from .driver_base import DriverBase
from pymodbus.client import ModbusTcpClient
import struct
import ipaddress


class TestDevice(DriverBase):

    def __init__(self, device_name: str):
        super().__init__(device_name)
        self.__set_client(ip="127.0.0.1", port=5020)
        self.hardware_para = ["ip", "port"]
        self.command = "测试设备控制命令"
        self.rev_f = modbus_frame.Framer()
        self.is_set_f = False
        self.default_frame()

    def default_frame(self):
        self.is_set_f = True
        self.rev_f.set_data(index=1, name="输入功率", type="float", size=4, formula=f"real_data=raw_data")
        self.rev_f.set_data(index=2, name="扭矩", type="float", size=4, formula=f"real_data=raw_data")
        self.rev_f.set_data(index=3, name="输出功率", type="float", size=4, formula=f"real_data=raw_data")
        self.curr_data = {"输入功率": 0, "扭矩": 0, "输出功率": 0}
        self.curr_para = {"负载量": 0, "测试设备控制命令": "write"}

    def updata_F_data(self, f_name: str, index: int, name: str, type: str, size: int, formula: str):
        if f_name == "rev_f":
            self.rev_f.data[index] = modbus_frame.Field(index, name, type, size, formula)

    def delete_F_data(self, f_name: str, index: int):
        if f_name == "rev_f":
            self.rev_f.data.pop(index)

    def __set_client(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.client = ModbusTcpClient(host=ip, port=port)

    def write_execute(self, para_dict: dict[str, any], write_count: int = 1) -> bool:
        """
        para_dict示例{"测试设备控制命令":"command", "负载量":float}
        command:"start_device","stop_device","P_mode","N_mode","N1_mode","write"
        """
        # address = 0  # 读取寄存器的起始地址
        # count = 3  # 读取的数字
        # coding = 4  # 编码格式占字节数，如果是float为4
        # slave = 1  # 设置从机地址
        # result = self.client.read_holding_registers(address=address, count=count * coding, slave=slave,
        #                                             timeout=5)  # 请求应该为00 01 00 00 00 06 01 03 00 01 00 0C

        if not self.conn_state:
            self.logger.error(f"服务器未连接! 非法写！")
            return False

        if self.command not in para_dict:
            command = "write"
        else:
            command = para_dict[self.command]
        if "负载量" not in para_dict:
            para_dict["负载量"] = 0

        if command == "start_device" or command == "启动":
            address = 0
            value = 1
            result = self.client.write_register(address, value, slave=1)
        elif command == "stop_device" or command == "停止":
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
            return False
        self.logger.info(f"发送指令：{command, value}")
        if result.isError():
            self.logger.error(f"发送失败！")
            return False
        else:
            # 确认写正确后，更改状态值
            if command == "start_device" or command == "启动":
                self.run_state = True
            elif command == "stop_device" or command == "停止":
                self.run_state = False
            for key in self.curr_para:
                self.curr_para[key] = para_dict[key]
            return True

    def connect(self) -> bool:
        try:
            if self.client.is_socket_open():
                self.conn_state = True
                return True
            self.conn_state = self.client.connect()
            if self.conn_state:
                self.logger.info(f"client连接到服务器{self.client}")
                return True
            else:
                self.logger.error(f"连接错误！")
                return False
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

    def recv_one(self, timeout: float = 1) -> bytes:
        self.client.comm_params.timeout_connect = timeout  # 设置接收超时时间，如果超时即使接收的字节数少于目标值也返回
        try:
            msg = self.client.recv(6)
            if len(msg) == 6:  # 数据头
                length = int.from_bytes(msg[-2:], byteorder="big", signed=False)
                msg += self.client.recv(length)
                if len(msg) == 6 + length:
                    self.logger.debug(f"收到的报文为：{msg.hex()}")
                    return msg
                else:
                    raise Exception(f"接收到的数据体长度不符合预期:{msg.hex()}")
            elif len(msg) == 0:
                return b""
            else:
                raise Exception(f"接收到的数据头长度不符合预期:{msg.hex()}")
        except Exception as e:
            self.logger.error(f"接收错误! error:{e}")
            return b""
        finally:
            pass  # 收尾

    def recv(self, timeout=0.02) -> bytes:
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
                    self.logger.warn(f"警告更新报文时间设置过短！请增大！ 报文更新周期大于{timeout * 10}s")
                break
        return msg

    def read_all(self, read_count=3) -> bool:
        if not self.is_set_f:
            return False
        for count in range(read_count):
            try:
                if not self.conn_state:
                    self.logger.error(f"服务器未连接! 非法读！")
                    return False
                result = self.recv()
                if not result:
                    raise Exception(f"接收失败! result：{result.hex()}")
                else:
                    state, e = self.rev_f.cofirm_framer(result)
                    if not state:
                        self.logger.error(f"查询回复解析报错{e}")
                        raise Exception(e)
                    # 数据检查完毕后开始读取数据
                    self.curr_data = self.rev_f.get_data()
                    return True
            except Exception as e:
                self.logger.error(f"error:{e},count：{count}")
        return False

    def handle_breakdown(self, breakdown: int) -> bool:
        try:
            if breakdown != 0:
                parameters = {"测试设备控制命令": "P_mode"}
                if not testdevice.write(parameters):
                    raise Exception(f"{parameters}")
                parameters = {"测试设备控制命令": "write", "load": float(0) / 10}  # 假设空载为0
                if not testdevice.write(parameters):
                    raise Exception(f"{parameters}")
                parameters = {"测试设备控制命令": "启动"}
                if not testdevice.write(parameters):
                    raise Exception(f"{parameters}")
            else:
                self.logger.error(f"未收到故障码！")
            return True
        except Exception as e:
            self.logger.error(f"故障处理模块报错！ error:{e}")
            self.logger.error(f"再次尝试空载！")
            parameters = {"测试设备控制命令": "P_mode"}
            testdevice.write(parameters)
            parameters = {"测试设备控制命令": "write", "load": float(0) / 10}  # 假设空载为0
            testdevice.write(parameters)
            parameters = {"测试设备控制命令": "启动"}
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
                    self.logger.info(f"ip地址更新为{value}")
                except ValueError:
                    return False
            elif key == "port":
                if type(value) == int:
                    selfport = value
                    self.logger.info(f"端口号更新为{value}")
                else:
                    return False
            else:
                self.logger.error(f"{key} 不是一个有效参数.")
        self.__set_client(selfip, selfport)
        return True

    def get_hardware_parameter(self) -> dict[str, any]:
        return {"ip": self.ip, "port": self.port}

    def load_config(self, F_config: dict) -> tuple[bool, None] | tuple[bool, Exception]:
        try:
            for key, value in F_config.items():
                if key == "rev_f":
                    self.rev_f.reset_all()
                    self.rev_f.load_framer(json.loads(value))
            self.logger.info(f"测试设备帧配置导入成功！")
            return True, None
        except Exception as e:
            self.logger.error(f"测试设备帧配置导入error！{e}")
        return False, e

    def export_config(self):
        return {"rev_f": json.dumps(self.pre_dict(self.rev_f.export_framer()))}

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

    def get_database_table(self):
        all_data = {}
        for _, value in self.rev_f.data.items():
            all_data[value.name] = value.type
        all_data["负载量"] = "float"
        return all_data

    def close_device(self):
        return self.write({"测试设备控制命令": "stop_device"})


if __name__ == "__main__":
    testdevice = TestDevice(device_name="TestDevice")
    testdevice.default_frame()
    testdevice.connect()
    # testdevice.update_hardware_parameter(para_dict={"ip": "127.0.0.1", "port": 504})
    # print(testdevice.connect())
    # testdevice.update_hardware_parameter(para_dict={"ip": "120.76.28.211", "port": 80})
    # parameters = {"test_device_command": "start_device"}
    # testdevice.write(parameters)
    # parameters = {"test_device_command": "write", "load": 200}
    while 1:
        if testdevice.read_all():
            print(testdevice.curr_data)
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
