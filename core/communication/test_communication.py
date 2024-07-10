from . import communicator
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
