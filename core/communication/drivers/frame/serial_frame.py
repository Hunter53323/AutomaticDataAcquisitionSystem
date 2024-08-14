# -*- coding:utf-8 -*-
import logging
from enum import Enum
from typing import Tuple

from sympy import symbols, Eq, solve, sympify


class Framer:
    def __init__(self):
        self.header = b"\xA5"
        self.addr = b"\xFF"
        self.cmd = b"\x00"
        self.len = 0
        self.data: dict[int, Field] = {}  # self.data[index] = Field(index, name, type, size, formula),int:Field
        self.check = 0
        self.tail = b"\x5A"
        self.logger = logging.getLogger(__name__)

    def str2byte(self, char: str, size=1) -> bytes:
        hex_str = bytes.fromhex(char)
        if len(hex_str) == size:
            # 将字节转换为十六进制字符串
            return hex_str
        else:
            raise ValueError(f"输入长度不是{size}个字节")

    def byte2str(self, char: bytes, size=1) -> str:
        if len(char) == size:
            return char.hex()
        else:
            raise ValueError(f"输入长度不是{size}个字节")

    def set_header(self, header: str) -> tuple[True, None] | tuple[False, Exception]:
        try:
            self.header = self.str2byte(header)
            return True, None
        except Exception as e:
            return False, e

    def set_addr(self, addr: str) -> tuple[bool, None] | tuple[bool, Exception]:
        try:
            self.addr = self.str2byte(addr)
            return True, None
        except Exception as e:
            return False, e

    def set_cmd(self, cmd: str) -> tuple[bool, None] | tuple[bool, Exception]:
        try:
            self.cmd = self.str2byte(cmd)
            return True, None
        except Exception as e:
            return False, e

    def set_tail(self, tail: str) -> tuple[bool, None] | tuple[bool, Exception]:
        try:
            self.tail = self.str2byte(tail)
            return True, None
        except Exception as e:
            return False, e

    def set_data(self, index: int, name: str, type: str, size: int, formula: str, **kwargs) -> tuple[bool, None] | \
                                                                                               tuple[bool, Exception]:
        try:
            if index in self.data:
                raise Exception(f"第{index}位置已存在数据{self.data[index].name}")
            temp_Field = Field(index, name, type, size, formula)
            state, e = temp_Field.evaluate_formula()
            if not state:
                raise Exception(e)
            state, e = temp_Field.evaluate_formula(False)
            if not state:
                raise Exception(e)
            self.data[index] = temp_Field
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
        self.header = b"\xA5"
        self.addr = b"\xFF"
        self.cmd = b"\x00"
        self.reset_data()
        self.tail = b"\x5A"
        return True

    def reset_data(self) -> bool:
        self.len = 0
        self.data = {}
        self.check = 0
        return True

    def export_data(self):
        data_dict = []
        for _, value in self.data.items():
            data_dict.append(vars(value))
        return data_dict

    def load_data(self, data_dict: list) -> bool:
        self.reset_data()
        for value in data_dict:
            self.set_data(**value)
        self.cal_len()
        return True

    def export_framer(self):
        return {"header": self.header, "tail": self.tail, "cmd": self.cmd, "addr": self.addr,
                "data": self.export_data()}

    def load_framer(self, framer: dict) -> tuple[bool, None] | tuple[bool, Exception]:
        try:
            self.set_header(framer["header"])
            self.set_tail(framer["tail"])
            self.set_addr(framer["addr"])
            self.set_cmd(framer["cmd"])
            self.load_data(framer["data"])
            return True, None
        except Exception as e:
            print(e)
            return False, e

    def get_data(self):
        real_data = {}
        for _, value in self.data.items():
            real_data[value.name] = value.real_data
        return real_data

    def encode_framer(self) -> bytes:  # human->computer
        all_msg = b""
        self.cal_len()
        all_msg += self.header + self.addr + self.cmd + self.len.to_bytes()
        for _, value in self.data.items():
            all_msg += value.encode_data()
        all_msg += self.check_check(all_msg).to_bytes() + self.tail
        print(all_msg.hex())
        return all_msg

    def gen_data(self, name: str, data: int):
        for _, value in self.data.items():
            if value.name == name:
                value.set_realdata(data)
                return True
        raise Exception(f"{name}不存在")

    def cofirm_framer(self, msg: bytes) -> tuple[bool, None] | tuple[bool, Exception]:
        try:
            if (
                    msg[0].to_bytes() == self.header
                    and msg[-1].to_bytes() == self.tail
                    and msg[1].to_bytes() == self.addr
                    and msg[2].to_bytes() == self.cmd
            ):
                # print(msg[-2])
                # print(self.check_check(msg[0:-2]))
                if msg[-2] == self.check_check(msg[0:-2]):
                    # 先假设字典有序
                    cur = 4
                    for key, value in self.data.items():
                        value.decode_data(msg[cur: cur + value.size])
                        cur += value.size
                    return True, None
                else:
                    raise Exception("校验错误")
            else:
                raise Exception("报文头、尾、地址不匹配")
        except Exception as e:
            return False, e

    def check_check(self, msg: bytes) -> int:
        # 初始化校验和为0
        checksum = 0
        # 对数据中的每个字节进行累加
        for data in msg:
            # if data == msg[1]:  # 如果校验和包括地址就去掉if
            #     continue
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
    def __init__(self, index: int, name: str, type: str, size: int, formula: str = ""):
        if type in Fieldtype._member_names_:
            self.type = type
        else:
            raise Exception(f"格式{type}还未支持")
        self.index = index
        self.name = name
        self.size = size
        self.formula = formula  # 格式为"real_data=(raw_data+2)/3"
        self.inv_formula = ""
        self.raw_data = 0
        self.real_data = 0

    def decode_data(self, data: bytes):
        if self.type == "int16":
            self.raw_data = int.from_bytes(data, byteorder="big", signed=False)
            self.evaluate_formula(to_real=True)
        elif self.type == "bit16" or self.type == "bit8":
            self.real_data = int.from_bytes(data, byteorder="big", signed=False)
            self.raw_data = self.real_data
        else:
            pass

    def encode_data(self) -> bytes:
        print(self.name, int(self.raw_data))
        return int(self.raw_data).to_bytes(self.size)

    def set_realdata(self, real_data: int):
        self.real_data = real_data
        if self.type == "int16":
            self.evaluate_formula(to_real=False)
        elif self.type == "bit16" or self.type == "bit8":
            self.raw_data = real_data
        else:
            pass

    def inverse_formula(self):
        raw_data_sym = symbols("raw_data")
        real_data_sym = symbols("real_data")
        expr = sympify(self.formula.split("=")[1])
        raw_data_inverse_expr = solve(Eq(real_data_sym, expr), raw_data_sym)[0]
        return f"raw_data={raw_data_inverse_expr}"

    def evaluate_formula(self, to_real=True) -> tuple[bool, None] | tuple[bool, Exception]:
        try:
            if self.type == "bit16" or self.type == "bit8":
                return True, None
            local_vars = {}
            if to_real:
                local_vars["raw_data"] = self.raw_data
                exec(self.formula, {}, local_vars)
                self.real_data = local_vars.get("real_data")
            else:
                if self.inv_formula == "":
                    self.inv_formula = self.inverse_formula()
                local_vars["real_data"] = self.real_data
                exec(self.inv_formula, {}, local_vars)
                self.raw_data = local_vars.get("raw_data")
            return True, None
        except Exception as e:
            print(e)
            return False, e


if __name__ == "__main__":
    ff = Framer()
    ff.set_data(index=1, name="speed", type="int16", size=2, formula="real_data=raw_data")
    ff.set_data(index=2, name="torp", type="int16", size=2, formula="real_data=raw_data")
    ff.set_data(index=3, name="power", type="int16", size=2, formula="real_data=raw_data")
    ff.set_data(index=4, name="breakdown", type="bit16", size=2, formula="")
    ff.set_data(index=5, name="test", type="bit8", size=1, formula="")
    one_f = ff.export_framer()
    print(one_f)
    author_f = Framer()
    author_f.load_framer(one_f)
    print(author_f.export_framer())
    # for _, v in ff.data.items():
    #     v.set_realdata(100)
    # ff.encode_framer()
    # ff.cofirm_framer(b'\xA5\xFF\x00\x03\x00\x01\x00\x02\x03\x03\x01\x02\xb4\x5A')
    print(ff.check_check(b"\x5a\xFF\x02\x0c\x00\x01\x00\x02\x00\x03\x00\x04\x00\x05\x00\x00"))
    # 一个查询回复报文5aFF020c00010002000300040005000076A5
    # data = ff.get_data()
    # print(data)
