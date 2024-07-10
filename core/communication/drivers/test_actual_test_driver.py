from . import testdevice
import pytest


class TestActualTestDriver:

    def test_connect(self):
        testdevice.update_hardware_parameter(para_dict={"ip": "127.0.0.1", "port": 504})
        assert testdevice.connect() == False
        result = testdevice.update_hardware_parameter(para_dict={"ip": "127.0.2.1"})
        assert result == True
        result = testdevice.update_hardware_parameter(para_dict={"ip": "337.0.0.1", "port": 503})
        assert result == False
        result = testdevice.update_hardware_parameter(para_dict={"ip": "127.0.0.1", "port": "503"})
        assert result == False
        result = testdevice.update_hardware_parameter(para_dict={"ip": "127.0.0.1", "port": 503})
        assert result == True
        assert testdevice.connect() == True

    def test_read(self):
        testdevice.read_all()
        print("Test read:", testdevice.curr_data)
        parameters = {"test_device_command": "start_device"}
        print("Test start:", testdevice.write(parameters))
        parameters = {"test_device_command": "stop_device"}
        print("Test stop:", testdevice.write(parameters))
        parameters = {"test_device_command": "P_mode"}
        print("Test P:", testdevice.write(parameters))
        parameters = {"test_device_command": "N_mode"}
        print("Test N:", testdevice.write(parameters))
        parameters = {"test_device_command": "N1_mode"}
        print("Test N1:", testdevice.write(parameters))
        parameters = {"test_device_command": "write", "load": 200}
        print("Test write:", testdevice.write(parameters))

    def test_disconnect(self):
        assert testdevice.disconnect() == True
