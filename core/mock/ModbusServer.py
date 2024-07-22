# -*- coding: utf-8 -*-
import logging
import random
import socket
import struct
import threading
import time

from pymodbus.transaction import ModbusSocketFramer

# Setup logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)


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
        self.ip = ip
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(5)
        print(f"Server listening on {self.ip}:{self.port}")
        self.run_server()

    def handle_client(self, conn: socket.socket, addr):
        print(f"Connected by {addr}")
        sendcount = 0
        try:
            while True:
                self.send_one(conn, sendcount)
                sendcount += 1
                time.sleep(0.05)
                self.recv_one(conn)
        except Exception as e:
            print(f"Connection with {addr} closed: {e}")
        finally:
            conn.close()

    def send_one(self, conn: socket.socket, count):
        torque = random.uniform(30000, 40000)
        speed = random.uniform(50000, 10000)
        voltage = random.uniform(200, 380)
        MESSAGE = build_modbus_tcp_message(torque=torque, speed=speed, voltage=voltage)
        print(f"发送的报文为：{MESSAGE.hex()},count:{count}")
        conn.sendall(MESSAGE)

    def recv_one(self, conn: socket.socket, timeout: float = 0.1):
        conn.settimeout(timeout)
        try:
            msg = conn.recv(6)
            if len(msg) == 6:
                length = int.from_bytes(msg[-2:], byteorder="big", signed=False)
                msg += conn.recv(length)
                if len(msg) == 6 + length:
                    print(f"收到的报文为：{msg.hex()}")
                    ack = self.modbusTCP_ack(msg)
                    conn.sendall(ack)
        except Exception as e:
            print(f"接收错误! error:{e}")
        finally:
            pass

    def modbusTCP_ack(self, msg):
        tid, pid, length, uid, fc = struct.unpack(">HHHBB", msg[:8])
        if fc == 0x06:
            return msg
        elif fc == 0x10:
            startRegister, numRegister = struct.unpack(">HH", msg[8:12])
            body = struct.pack(">HH", startRegister, numRegister)
            length = len(body) + 2
            header = struct.pack(">HHHBB", tid, pid, length, uid, fc)
            return header + body

    def run_server(self):
        try:
            while True:
                conn, addr = self.server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.start()
        except KeyboardInterrupt:
            print("Server is shutting down.")
        finally:
            self.server_socket.close()


if __name__ == "__main__":
    server = Tcpserver(ip="127.0.0.1", port=5020)
