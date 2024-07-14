# -*- coding: utf-8 -*-
import logging
import socket
import struct
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


def run_server():
    datablock = ModbusSequentialDataBlock(0x00, [0] * 100)
    context = ModbusSlaveContext(
        di=datablock,
        co=datablock,
        hr=datablock,
        ir=datablock,
    )

    # Build data storage
    context = ModbusServerContext(slaves=context, single=True)

    address = ("127.0.0.1", 5020)

    StartTcpServer(framer=CustomModbusFramer, address=address, context=context)


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


class Tcpserver():
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('127.0.0.1', 5021))
        self.s.listen(1)
        self.conn, self.addr = self.s.accept()

    def run_server(self):
        print('Connected by', self.addr)
        for torque in range(0, 40000):
            MESSAGE = build_modbus_tcp_message(torque=float(torque) / 100)
            self.conn.sendall(MESSAGE)
            # time.sleep(0.02)
        for speed in range(0, 40000):
            MESSAGE = build_modbus_tcp_message(speed=float(speed) / 2)
            print(MESSAGE.hex())
            self.conn.sendall(MESSAGE)
            # time.sleep(0.05)
        for voltage in range(0, 40000):
            MESSAGE = build_modbus_tcp_message(voltage=float(voltage) / 2)
            print(MESSAGE.hex())
            self.conn.sendall(MESSAGE)
            # time.sleep(0.05)


if __name__ == "__main__":
    try:
        server = Tcpserver()
        server.run_server()#模拟一直发
        run_server()#模拟收
    except Exception as e:
        print(e)
        run_server()
