import socket
import struct
import time

from . import testdevice
import pytest


class TestActualTestDriver:

    def test_read_all(self):
        testdevice.update_hardware_parameter(para_dict={"ip": "127.0.0.1", "port": 5021})
        for _ in range(120000):
            assert testdevice.read_all() == True


    def test_connect(self):
        testdevice.update_hardware_parameter(para_dict={"ip": "127.0.0.1", "port": 5020})
        assert testdevice.connect() == True
        result = testdevice.update_hardware_parameter(para_dict={"ip": "127.0.2.1"})
        assert result == True
        result = testdevice.update_hardware_parameter(para_dict={"ip": "337.0.0.1", "port": 503})
        assert result == False
        result = testdevice.update_hardware_parameter(para_dict={"ip": "127.0.0.1", "port": "503"})
        assert result == False
        result = testdevice.update_hardware_parameter(para_dict={"ip": "127.0.0.1", "port": 5020})
        assert result == True
        assert testdevice.connect() == True

    def test_write(self):
        parameters = {"test_device_command": "start_device"}
        assert testdevice.write(parameters)==True
        parameters = {"test_device_command": "stop_device"}
        assert testdevice.write(parameters) == True
        parameters = {"test_device_command": "P_mode"}
        assert testdevice.write(parameters) == True
        parameters = {"test_device_command": "N_mode"}
        assert testdevice.write(parameters) == True
        parameters = {"test_device_command": "N1_mode"}
        assert testdevice.write(parameters) == True
        parameters = {"test_device_command": "asdafasg"}#����ָ��
        assert testdevice.write(parameters) == False
        for load in range(20000):
            parameters = {"test_device_command": "write", "load": float(load)/10}
            assert testdevice.write(parameters) == True
    def test_disconnect(self):
        assert testdevice.disconnect() == True
