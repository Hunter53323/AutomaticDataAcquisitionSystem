# -*- coding: utf-8 -*-
import logging
import random
import socket
import struct
import threading
import time

from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusSocketFramer

# Setup logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)


class CustomModbusFramer(ModbusSocketFramer):
    def processIncomingPacket(self, data, callback, slave, **kwargs):
        log.debug("Received data: " + str(data))
        log.debug("Received header: " + str(self._header))
        return super().processIncomingPacket(data, callback, slave)

    def buildPacket(self, message):
        packet = super().buildPacket(message)
        log.debug("Sending data: " + str(packet))
        return packet


def build_modbus_tcp_message(torque=0.01, speed=0.1, voltage=0.01):
    # 构建报文头
    tid = 0  # 事务标识符
    pid = 0  # 协议标识符
    length = 15  # 长度字段
    uid = 1  # 单元标识符
    fc = 3  # 功能码
    data_size = 3 * 4
    header = struct.pack(">HHHBBB", tid, pid, length, uid, fc, data_size)
    # 构建数据
    data = struct.pack(">fff", torque, speed, voltage)
    # 返回报文
    return header + data


class Tcpserver:
    def __init__(self, ip="127.0.0.1", port=5020):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((ip, port))
        self.s.listen(1)
        self.conn, self.addr = self.s.accept()
        print("Connected by", self.addr)
        self.sendcount = 0
        self.run_server()

    def send_one(self):
        torque = random.uniform(0, 40000)
        speed = random.uniform(0, 10000)
        voltage = random.uniform(0, 380)
        MESSAGE = build_modbus_tcp_message(torque=torque, speed=speed, voltage=voltage)
        print(f"发送的报文为：{MESSAGE.hex()},count:{self.sendcount}")
        self.sendcount += 1
        self.conn.sendall(MESSAGE)

    def recv_one(self, timeout: float = 0.1):
        self.conn.settimeout(timeout)  # 设置接收超时时间，如果超时即使接收的字节数少于目标值也返回
        try:
            msg = self.conn.recv(6)
            if len(msg) == 6:  # 数据头
                length = int.from_bytes(msg[-2:], byteorder="big", signed=False)
                msg += self.conn.recv(length)
                if len(msg) == 6 + length:
                    print(f"收到的报文为：{msg.hex()}")
                    ack = self.modbusTCP_ack(msg)
                    self.conn.sendall(ack)
                    return msg
                else:
                    raise Exception(f"接收到的数据长度不符合预期:{msg.hex()}")
            else:
                raise Exception(f"接收到的数据头长度不符合预期:{msg.hex()}")
        except Exception as e:
            print(f"接收错误! error:{e}")
            return
        finally:
            pass  # 收尾

    def modbusTCP_ack(self, msg):
        tid, pid, length, uid, fc = struct.unpack(">HHHBB", msg[:8])
        if fc == 0x06:
            return msg
        elif fc == 0x10:
            startRegister, numRegister = struct.unpack(">HH", msg[8:12])
            body = struct.pack(">HH", startRegister, numRegister)
            length = len(body) + 2  # 动态计算长度，包括Unit Identifier和Function Code
            header = struct.pack(">HHHBB", tid, pid, length, uid, fc)
            # 返回报文
            return header + body

    def run_server(self):
        while True:
            self.send_one()  # 定时发
            time.sleep(0.05)
            self.recv_one()
            # time.sleep(0.05)


if __name__ == "__main__":
    try:
        server = Tcpserver(ip="127.0.0.1", port=5020)
    except Exception as e:
        print(e)
# TODO:服务器退出之后继续运行，除非手动退出，手动退出的时候也需要能够正常退出
