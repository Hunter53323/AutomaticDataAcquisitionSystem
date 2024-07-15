from .actual_test_driver import TestDevice
from .fan_drive_module import FanDriver

testdevice = TestDevice(device_name="TestDevice", data_list=["motor_input_power", "torque", "motor_output_power"], para_list=["load"])
# 控制命令test_device_command

fandriver = FanDriver(
    device_name="FanDriver",
    data_list=[
        "target_speed",
        "actual_speed",
        "dc_bus_voltage",
        "U_phase_current",
        "power",
        "breakdown",
    ],
    para_list=[
        "set_speed",
        "speed_loop_compensates_bandwidth",
        "current_loop_compensates_bandwidth",
        "observer_compensates_bandwidth",
    ],
    device_address=b"\x01",
    cpu="M0",
    port="COM9",
)
# 控制命令fan_command
