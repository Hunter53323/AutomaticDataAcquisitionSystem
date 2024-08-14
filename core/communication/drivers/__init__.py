from .actual_test_driver import TestDevice
from .fan_drive_module import FanDriver

testdevice = TestDevice(device_name="TestDevice")
# 控制命令 "测试设备控制命令"

fandriver = FanDriver(device_name="FanDriver")
# 控制命令  "控制命令"
