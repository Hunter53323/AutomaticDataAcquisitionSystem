from .actual_test_driver import TestDevice
from .fan_drive_module import FanDriver

testdevice = TestDevice(
    device_name="TestDevice", data_list=["motor_input_power", "torque", "motor_output_power"], para_list=["test_device_command", "load"]
)

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
        "fan_command",
        "set_speed",
        "speed_loop_compensates_bandwidth",
        "current_loop_compensates_bandwidth",
        "observer_compensates_bandwidth",
    ],
    device_address=b"\x01",
    cpu="M0",
    port="COM9",
)

# from .test_driver1 import TestDriver1
# from .test_driver2 import TestDriver2
#
# driver1 = TestDriver1(
#     "TestDevice1",
#     [
#         "data1",
#         "data2",
#         "moredata1",
#         "moredata2",
#         "moredata3",
#         "moredata4",
#         "moredata5",
#         "moredata6",
#         "moredata7",
#     ],
#     ["para1", "para2"],
# )
# driver2 = TestDriver2("TestDevice2", ["data3", "data4"], ["para3", "para4"])
