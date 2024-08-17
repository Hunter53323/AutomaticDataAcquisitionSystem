import serial
import time
import struct
from fan import Fan

state = False

breakdowncnt = 1


def handle_command(data: bytes, fan: Fan, testbreakdown: bool = False):
    # 根据命令字符串进行处理
    byte0 = b"\x5A"
    byte1 = b"\xFF"
    try:
        if data[2].to_bytes() == b"\x01":
            print("收到控制命令")
            # 控制命令回复
            byte2 = b"\x01"
            byte3 = b"\x01"
            data_checksum = calculate_checksum(data[0:13])
            # print(data_checksum)
            # print(data[13].to_bytes())
            if data_checksum == data[13].to_bytes():
                # 执行电机控制
                speed = int.from_bytes(data[5:7])
                control = data[4]
                if control == 1:
                    state = True
                elif control == 2:
                    state = False
                    speed = 0
                elif control == 4:
                    state = fan.state
                elif control == 0:
                    state = fan.state
                else:
                    raise Exception("control error")
                fan.control(state, speed)

                byte4 = b"\x01"
            else:
                print("checksum error")
                byte4 = b"\x02"
            byte5 = calculate_checksum(byte0, byte1, byte2, byte3, byte4)
            if byte5 != b"\x5C" and byte5 != b"\x5D":
                raise Exception("checksum error")
            byte6 = b"\xA5"
            response = byte0 + byte1 + byte2 + byte3 + byte4 + byte5 + byte6
        elif data[2].to_bytes() == b"\x02":
            # 查询命令
            print("收到查询命令")
            byte2 = b"\x02"
            byte3 = b"\x0C"
            # 自定义的设置查询数据
            # target_speed, actual_speed, dc_bus_voltage, U_phase_current, power, breakdown = fan.read()
            target_speed, actual_speed, _, _, _, _ = fan.read()
            # target_speed = 165
            # actual_speed = 300
            dc_bus_voltage = 50
            U_phase_current = 100
            power = 30
            byte4and5 = struct.pack(">H", target_speed)
            byte6and7 = struct.pack(">H", actual_speed)
            byte8and9 = struct.pack(">H", dc_bus_voltage)
            byte10and11 = struct.pack(">H", U_phase_current)
            byte12and13 = struct.pack(">H", power)

            if testbreakdown:  # 模拟故障
                global breakdowncnt
                byte14and15 = breakdowncnt.to_bytes(2, byteorder="big", signed=False)
                byte14 = byte14and15[1].to_bytes()
                byte15 = byte14and15[0].to_bytes()
                breakdowncnt += 1
            else:
                byte14 = b"\x00"  # 不模拟故障
                byte15 = b"\x00"

            byte16 = calculate_checksum(byte0, byte1, byte2, byte3, byte4and5 + byte6and7 + byte8and9 + byte10and11 + byte12and13 + byte14 + byte15)
            byte17 = b"\xA5"
            response = (
                byte0 + byte1 + byte2 + byte3 + byte4and5 + byte6and7 + byte8and9 + byte10and11 + byte12and13 + byte14 + byte15 + byte16 + byte17
            )
        else:
            byte2 = b"\x00"
            byte3 = b"\x00"
            byte5 = b"\x00"
            byte6 = b"\xA5"
            response = byte0 + byte1 + byte2 + byte3 + byte5 + byte6
        return response
    except Exception as e:
        print(e)
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


def read_msg(ser: serial.Serial):
    while ser.in_waiting < 4:
        time.sleep(0.005)
    recv = ser.read(4)
    while ser.in_waiting < recv[3] + 2:
        time.sleep(0.005)
    recv = recv + ser.read(recv[3] + 2)
    return recv


if __name__ == "__main__":
    # 配置串行端口
    fan = Fan()
    ser = serial.Serial("COM10", 9600, timeout=10)  # 请替换为您的串行端口和波特率
    fan.thread_start()
    print("服务器启动")

    try:
        while True:
            # 检查是否有数据
            # print(ser.in_waiting)
            if ser.in_waiting:
                data = read_msg(ser)
                print(f"收到命令: {data.hex()}")

                # 处理命令
                # 在处理之前应该检查报文是否为有效报文！
                response = handle_command(data, fan, False)
                # print(time.time())
                print("发送回复:", response.hex())
                ser.write(response)

            # 添加一些延迟，避免过快的轮询
            # time.sleep(0.1)
    except KeyboardInterrupt:
        fan.stop()
        print("退出程序")
    finally:
        ser.close()  # 关闭串行端口

# 校验和：帧头、命令码、总包数、当前包数、数据长度、数据
# 字节序列想要完整打印就data.hex()，取出来的单个字节想完整打印就是data[0].to_bytes()，for循环中可以直接打印
