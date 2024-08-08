# -*- coding:utf-8 -*-
import logging
from enum import Enum

from sympy import symbols, Eq, solve, sympify


class Framer:
    def __init__(self):
        self.header = b'\xA5'
        self.addr = b'\xFF'
        self.cmd = b'\x00'
        self.len = 0
        self.data = {}  # self.data[index] = Field(index, name, type, size, formula),int:Field
        self.check = 0
        self.tail = b'\x5A'
        self.logger = logging.getLogger(__name__)

    def check2byte(self, char: bytes, size=1) -> bool:
        if len(char) == size:
            # 将字节转换为十六进制字符串
            hex_str = char.hex()
            # 检查十六进制字符串是否为单字节
            if len(hex_str) == 2 and all(c in '0123456789abcdefABCDEF' for c in hex_str):
                return True
            else:
                raise ValueError("输入不是有效的单字节十六进制码")
        else:
            raise ValueError(f"输入长度不是{size}个字节")

    def set_header(self, header: bytes) -> tuple[True, None] | tuple[False, Exception]:
        try:
            self.check2byte(header)
            self.header = header
            return True, None
        except Exception as e:
            return False, e

    def set_addr(self, addr: bytes) -> tuple[bool, None] | tuple[bool, Exception]:
        try:
            self.check2byte(addr)
            self.addr = addr
            return True, None
        except Exception as e:
            return False, e

    def set_cmd(self, cmd: bytes) -> tuple[bool, None] | tuple[bool, Exception]:
        try:
            self.check2byte(cmd)
            self.cmd = cmd
            return True, None
        except Exception as e:
            return False, e

    def set_tail(self, tail: bytes) -> tuple[bool, None] | tuple[bool, Exception]:
        try:
            self.check2byte(tail)
            self.tail = tail
            return True, None
        except Exception as e:
            return False, e

    def set_data(self, index: int, name: str, type: str, size: int, formula: str, **kwargs) -> tuple[bool, None] | \
                                                                                               tuple[
                                                                                                   bool, Exception]:
        try:
            if index in self.data:
                raise Exception(f"第{index}位置已存在数据{self.data[index].name}")
            self.data[index] = Field(index, name, type, size, formula)
            return True, None
        except Exception as e:
            print(e)
            return False, e

    def cal_len(self) -> int:
        num = 0
        for key, value in self.data.items():
            num += value.size
        self.len = num
        return num

    def reset_all(self) -> bool:
        self.header = b'\xA5'
        self.addr = b'\xFF'
        self.cmd = b'\x00'
        self.reset_data()
        self.tail = b'\x5A'
        return True

    def reset_data(self) -> bool:
        self.len = 0
        self.data = {}
        self.check = 0
        return True

    def export_data(self):
        data_dict = {}
        for key, value in self.data.items():
            data_dict[key] = vars(value)
        return data_dict

    def load_data(self, data_dict: dict) -> bool:
        self.reset_data()
        for _, value in data_dict.items():
            self.set_data(**value)
        self.cal_len()
        return True

    def get_data(self):
        real_data = {}
        for _, value in self.data.items():
            if value.type == ("bit16" or "bit8"):
                pass
            real_data[value.name] = value.real_data
        return real_data

    def encode_data(self) -> bytes:  # human->computer
        all_msg = b''
        all_msg += self.header + self.addr + self.cmd + self.tail
        print(all_msg.hex())
        return all_msg

    def get_breakdown(self,breakdown):
        pass

    def handle_breakdown(self,breakdown):
        pass

    def cofirm_framer(self, msg: bytes):
        if msg[0].to_bytes() == self.header and msg[-1].to_bytes() == self.tail and msg[1].to_bytes() == self.addr and \
                msg[2].to_bytes() == self.cmd:
            if msg[-2] == self.check_check(msg[0:-2]):
                # 先假设字典有序
                cur = 4
                for key, value in self.data.items():
                    value.updata_data(msg[cur:cur + value.size])
                    cur += value.size
            else:
                raise Exception("校验错误")
        else:
            raise Exception("报文头、尾、地址不匹配")

    def check_check(self, msg: bytes) -> int:
        # 初始化校验和为0
        checksum = 0
        # 对数据中的每个字节进行累加
        for data in msg:
            if data == msg[1]:
                continue
            checksum += data
        # 取累加结果的低8位
        checksum_low8 = checksum & 0xFF
        # print(checksum_low8.to_bytes())
        return checksum_low8


class Fieldtype(Enum):
    int16 = 1
    bit16 = 2
    bit8 = 3


class Field:
    def __init__(self, index: int, name: str, type: str, size: int, formula: str):
        if type in Fieldtype._member_names_:
            self.type = type
        else:
            raise Exception(f"格式{type}还未支持")
        self.index = index
        self.name = name
        self.size = size
        self.formula = formula  # 格式为"real_data=(raw_data+2)/3"
        self.inv_formula = self.inverse_formula()
        self.raw_data = 0  # bytes([0]*self.size)
        self.real_data = 0

    def updata_data(self, data: bytes):
        if self.type == "int16":
            self.raw_data = int.from_bytes(data, byteorder="big", signed=False)
            self.evaluate_formula(to_real=True)
        elif self.type == ("bit16" or "bit8"):
            self.real_data = int.from_bytes(data, byteorder="big", signed=False)
        else:
            pass

    def inverse_formula(self):
        if self.type == ("bit16" or "bit8"):
            return ""
        elif self.type == "int16":
            raw_data_sym = symbols('raw_data')
            real_data_sym = symbols('real_data')
            expr = sympify(self.formula.split('=')[1])
            raw_data_inverse_expr = solve(Eq(real_data_sym, expr), raw_data_sym)[0]
            return f"raw_data={raw_data_inverse_expr}"

    def evaluate_formula(self, to_real=True):
        local_vars = {}
        if to_real:
            local_vars['raw_data'] = self.raw_data
            exec(self.formula, {}, local_vars)
            self.real_data = local_vars.get('real_data')
            return self.real_data
        else:
            local_vars['real_data'] = self.real_data
            exec(self.inv_formula, {}, local_vars)
            self.raw_data = local_vars.get('raw_data')
            return self.raw_data


if __name__ == "__main__":
    ff = Framer()
    ff.set_data(index=1, name="speed", type="int16", size=2, formula="real_data=(raw_data+2)/3")
    ff.set_data(index=2, name="torp", type="int16", size=2, formula="real_data=(raw_data+2)/3")
    ff.set_data(index=3, name="power", type="int16", size=2, formula="real_data=(raw_data+2)/3")
    ff.set_data(index=4, name="breakdown", type="bit16", size=2, formula="")
    ff.cofirm_framer(b'\xA5\xFF\x00\x03\x00\x01\x00\x02\x03\x03\x01\x02\xb4\x5A')
    data = ff.get_data()
    print(data)
    ff.encode_data()
