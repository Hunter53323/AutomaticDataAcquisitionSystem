from core.communication import communicator
from core.auto_collection import auto_collector
import time
import random


def test_communicator_connect():
    assert communicator.connect() == True


def test_communicator_start_read_all():
    assert communicator.start_read_all() == True


def test_communicator_read():
    print("读取全部数据测试:", communicator.read())
    print("读取实际转速:", communicator.read(["actual_speed"]))
    print("读取参数测试:", communicator.get_curr_para())


def test_communicator_write_and_read():
    assert communicator.write({"fan_command": "start", "set_speed": 100, "test_device_command": "start_device"}) == True
    time.sleep(0.1)
    print("读取全部数据测试:", communicator.read())
    print("读取实际转速:", communicator.read(["actual_speed"]))
    print("读取参数测试:", communicator.get_curr_para())
    print("读取给定转速测试:", communicator.get_curr_para(["set_speed"]))

    assert communicator.write({"set_speed": 200}) == True

    time.sleep(0.1)
    print("读取全部数据测试:", communicator.read())
    print("读取实际转速:", communicator.read(["actual_speed"]))
    print("读取参数测试:", communicator.get_curr_para())
    print("读取给定转速测试:", communicator.get_curr_para(["set_speed"]))

    assert communicator.write({"fan_command": "stop", "test_device_command": "stop_device"}) == True


def test_stop():
    assert communicator.stop_read_all() == True
    assert communicator.disconnect() == True


def test_communicator():
    print("连接设备，并启动读取功能")
    communicator.connect()
    communicator.start_read_all()
    print()

    print("读取全部 Data 测试")
    print(communicator.read())
    print()
    print("读取单个 Data 测试")
    print(communicator.read(["data1"]))
    print()

    print("读取 Para 测试")
    print(communicator.get_curr_para())
    print()

    print("设置 Para 测试")
    communicator.write({"para1": 100, "para3": 999, "para2": 12312})
    print()

    print("读取修改后全部 Para 测试")
    print(communicator.get_curr_para())
    print()
    print("读取修改后多个 Para 测试")
    print(communicator.get_curr_para(["para1", "para3"]))

    communicator.stop_read_all()


def test_auto_collector():
    communicator.connect()
    communicator.start_read_all()
    auto_collector.init_para_pool(
        {
            "para1": [1, 2, 3, 4],
            "para2": [100, 200, 300, 400],
            "para3": [5, 15, 25],
            "para4": [7, 8, 9],
        }
    )
    auto_collector.auto_collect()


if __name__ == "__main__":
    test_communicator_connect()
    test_communicator_start_read_all()
    test_communicator_read()
    test_communicator_write_and_read()
    test_stop()
    # test_communicator()
    # test_auto_collector()
