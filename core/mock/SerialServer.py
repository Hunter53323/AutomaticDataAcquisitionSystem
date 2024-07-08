import serial
import time
import struct


def handle_command(data: bytes):
    # 根据命令字符串进行处理
    byte0 = b"\x5A"
    byte1 = b"\xFF"
    if data[2].to_bytes() == b"\x01":
        # 控制命令
        byte2 = b"\x01"
        byte3 = b"\x01"
        data_checksum = calculate_checksum(data[0:13])
        if data_checksum == data[13].to_bytes():
            byte4 = b"\x01"
        else:
            byte4 = b"\x02"
        byte5 = calculate_checksum(byte0, byte1, byte2, byte3, byte4)
        if byte5 != b"\x5C" and byte5 != b"\x5D":
            raise Exception("checksum error")
        byte6 = b"\xA5"
        response = byte0 + byte1 + byte2 + byte3 + byte4 + byte5 + byte6
    elif data[2].to_bytes() == b"\x02":
        # 查询命令
        byte2 = b"\x02"
        byte3 = b"\x0C"
        # 自定义的设置查询数据
        target_speed = 200
        actual_speed = 300
        dc_bus_voltage = 50
        U_phase_current = 100
        power = 30
        byte4and5 = struct.pack(">H", target_speed)
        byte6and7 = struct.pack(">H", actual_speed)
        byte8and9 = struct.pack(">H", dc_bus_voltage)
        byte10and11 = struct.pack(">H", U_phase_current)
        byte12and13 = struct.pack(">H", power)
        byte14 = b"\x00"
        byte15 = b"\x00"
        byte16 = calculate_checksum(byte0, byte1, byte2, byte3, byte4and5 + byte6and7 + byte8and9 + byte10and11 + byte12and13 + byte14 + byte15)
        byte17 = b"\xA5"
        response = byte0 + byte1 + byte2 + byte3 + byte4and5 + byte6and7 + byte8and9 + byte10and11 + byte12and13 + byte14 + byte15 + byte16 + byte17
    else:
        byte2 = b"\x00"
        byte3 = b"\x00"
        byte5 = b"\x00"
        byte6 = b"\xA5"
        response = byte0 + byte1 + byte2 + byte3 + byte5 + byte6
    return response


def calculate_checksum(*args: bytes) -> bytes:
    # 初始化校验和为0
    checksum = 0

    # 对数据中的每个字节进行累加
    for data in args:
        for byte in data:
            checksum += byte

    # 取累加结果的低8位
    checksum_low8 = checksum & 0xFF

    return bytes([checksum_low8])


if __name__ == "__main__":
    # 配置串行端口
    ser = serial.Serial("COM10", 9600, timeout=10)  # 请替换为您的串行端口和波特率
    print("服务器启动")

    try:
        while True:
            # 检查是否有数据
            if ser.in_waiting:
                data = ser.read_until(b"\x5A")
                print(f"收到命令: {data.hex()}")

                # 处理命令
                response = handle_command(data)
                ser.write(response)

            # 添加一些延迟，避免过快的轮询
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("退出程序")
    finally:
        ser.close()  # 关闭串行端口


# 校验和：帧头、命令码、总包数、当前包数、数据长度、数据
# 字节序列想要完整打印就data.hex()，取出来的单个字节想完整打印就是data[0].to_bytes()，for循环中可以直接打印
