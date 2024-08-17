# -*- coding:utf-8 -*-
import logging
import struct
from enum import Enum
from typing import Tuple

from sympy import symbols, Eq, solve, sympify


class Framer:
    def __init__(self):
        # self.tid = b"\x00\x00"
        self.pid = b"\x00\x00"
        self.length = 0
        self.uid = 1
        self.fc = b"\x03"
        self.begin_byte = 0
        self.data = {}  # self.data[index] = Field(index, name, type, size, formula),int:Field

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

    def set_begin_byte(self, begin_byte: int) -> tuple[bool, None] | tuple[bool, Exception]:
        try:
            if isinstance(begin_byte, int):
                self.begin_byte = begin_byte
                return True, None
            else:
                raise Exception(f"开始字节类型输入错误{type(begin_byte)}")
        except Exception as e:
            return False, e

    def set_tid(self, tid: str) -> tuple[True, None] | tuple[False, Exception]:
        try:
            self.tid = self.str2byte(tid, 2)
            return True, None
        except Exception as e:
            return False, e

    def set_uid(self, uid: str) -> tuple[bool, None] | tuple[bool, Exception]:
        try:
            self.uid = self.str2byte(uid)
            return True, None
        except Exception as e:
            return False, e

    def set_fc(self, fc: str) -> tuple[bool, None] | tuple[bool, Exception]:
        try:
            self.fc = self.str2byte(fc)
            return True, None
        except Exception as e:
            return False, e

    def set_pid(self, pid: str) -> tuple[bool, None] | tuple[bool, Exception]:
        try:
            self.pid = self.str2byte(pid, 2)
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
        num = 1
        for key, value in self.data.items():
            num += value.size
        self.length = num
        return num

    def reset_all(self) -> bool:
        self.tid = b"\x00\x00"
        self.pid = b"\x00\x00"
        self.length = 0
        self.uid = b"\x01"
        self.fc = b"\x03"
        self.reset_data()
        return True

    def reset_data(self) -> bool:
        self.data: dict[int, Field] = {}  # self.data[index] = Field(index, name, type, size, formula),int:Field
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
        self.cal_len()
        return {"tid": self.tid, "pid": self.pid, "length": self.length, "uid": self.uid, "fc": self.fc,
                "data": self.export_data()}

    def load_framer(self, framer: dict) -> tuple[bool, None] | tuple[bool, Exception]:
        try:
            self.set_tid(framer["tid"])
            self.set_pid(framer["pid"])
            self.set_uid(framer["uid"])
            self.set_fc(framer["fc"])
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
        all_msg += self.tid + self.pid + self.length.to_bytes(2) + self.uid + self.fc + len(self.data).to_bytes()
        for _, value in self.data.items():
            all_msg += value.encode_data()
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
            if len(msg) == sum(value.size for _, value in self.data.items()):
                # 先假设字典有序
                cur = 0
                for key, value in self.data.items():
                    value.decode_data(msg[cur: cur + value.size])
                    cur += value.size
                return True, None
            else:
                raise Exception("数据个数错误")
            # tid, pid, length, uid, fc, data_size = struct.unpack(">HHHBBB", msg[:9])
            # if pid.to_bytes(2) == self.pid and uid.to_bytes() == self.uid and fc.to_bytes() == self.fc:
            #     if data_size == sum(value.size for _, value in self.data.items()):
            #         # 先假设字典有序
            #         cur = 9
            #         for key, value in self.data.items():
            #             value.decode_data(msg[cur: cur + value.size])
            #             cur += value.size
            #         self.tid = tid  # 更新标识方便回复
            #         return True, None
            #     else:
            #         raise Exception("数据个数错误")
            # else:
            #     raise Exception("协议标识、设备地址、功能码不匹配")
        except Exception as e:
            return False, e


class Fieldtype(Enum):
    int16 = 1
    bit16 = 2
    bit8 = 3
    float = 4


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
        self.raw_data = 0  # bytes([0]*self.size)
        self.real_data = 0

    def decode_data(self, data: bytes):
        if self.type == "int16":
            self.raw_data = int.from_bytes(data, byteorder="big", signed=False)
            self.evaluate_formula(to_real=True)
        elif self.type == "bit16" or self.type == "bit8":
            self.real_data = int.from_bytes(data, byteorder="big", signed=False)
            self.raw_data = self.real_data
        elif self.type == "float":
            self.raw_data = struct.unpack(">f", data)[0]
            self.evaluate_formula(to_real=True)
        else:
            pass

    def encode_data(self) -> bytes:
        print(self.name, self.raw_data)
        return self.raw_data.to_bytes(self.size)

    def set_realdata(self, real_data: int):
        self.real_data = real_data
        if self.type == "int16" or self.type == "float":
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
    ff.set_data(index=1, name="speed", type="float", size=4, formula="real_data=raw_data")
    ff.set_data(index=2, name="torp", type="float", size=4, formula="real_data=raw_data")
    ff.set_data(index=3, name="power", type="float", size=4, formula="real_data=raw_data")
    ff.set_data(index=4, name="breakdown", type="float", size=4, formula="real_data=raw_data")
    ff.set_data(index=5, name="test", type="float", size=4, formula="real_data=raw_data")
    one_f = ff.export_framer()
    print(one_f)
    author_f = Framer()
    author_f.load_framer(one_f)
    print(author_f.export_framer())
    # for _, v in ff.data.items():
    #     v.set_realdata(100)
    # ff.encode_framer()
    # ff.cofirm_framer(b'\xA5\xFF\x00\x03\x00\x01\x00\x02\x03\x03\x01\x02\xb4\x5A')
    # 一个查询回复报文5aFF020c00010002000300040005000076A5
    # data = ff.get_data()
    # print(data)
