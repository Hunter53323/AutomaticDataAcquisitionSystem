from . import control
<<<<<<< HEAD
=======
from core.communication import communicator
from flask import request, jsonify
>>>>>>> 2af0e0f2a1be68e0adac5e3c1623b72f595c9ec1


@control.route("/testdevice", methods=["POST"])
# 测试设备控制
def testdevice_control():
    """
    测试设备控制
    """
    test_device = communicator.find_driver("TestDevice")
    command = request.form.get("command")
    if command == "start":
        status = test_device.write({"test_device_command": "start_device"})
    elif command == "stop":
        status = test_device.write({"test_device_command": "stop_device"})
    elif command == "P_mode":
        status = test_device.write({"test_device_command": "P_mode"})
    elif command == "N_mode":
        status = test_device.write({"test_device_command": "N_mode"})
    elif command == "N1_mode":
        status = test_device.write({"test_device_command": "N1_mode"})
    else:
        status = False

    return jsonify({"status": status}), 200


@control.route("/testdevice/set", methods=["GET", "POST"])
# 对测试设备参数进行设置，修改设备名称，D轴电感、Q轴电感等参数
def set_testdevice():
    """
    POST接收到的数据格式为：{"para_name1": value, "para_name2": value}
    返回的是{"status": True or False}
    GET接收返回的是当前的设备参数，数据格式同上，为全部参数
    """
    if request.method == "GET":
        return jsonify(communicator.get_hardware_parameter(device_name="TestDevice")), 200
    else:
        status = communicator.update_hardware_parameter(device_name="TestDevice", para_dict=request.json)
        return jsonify({"status": status}), 200


@control.route("/fan", methods=["POST"])
# 风机控制
def fan_control():
    """
    接收"command": "start", "stop", "clear_breakdown"
    返回{"status": True or False}
    """
    fan = communicator.find_driver("FanDriver")
    command = request.form.get("command")
    if command == "start":
        status = fan.write(
            {
                "fan_command": "start",
                "set_speed": 100,
                "speed_loop_compensates_bandwidth": 0,
                "current_loop_compensates_bandwidth": 0,
                "observer_compensates_bandwidth": 0,
            }
        )
    elif command == "stop":
        status = fan.write(
            {
                "fan_command": "stop",
                "set_speed": 0,
                "speed_loop_compensates_bandwidth": 0,
                "current_loop_compensates_bandwidth": 0,
                "observer_compensates_bandwidth": 0,
            }
        )
    elif command == "clear_breakdown":
        status = fan.handle_breakdown(1)
    else:
        status = False

    return jsonify({"status": status}), 200


@control.route("/fan/set", methods=["GET", "POST"])
# 对风机进行设置，修改端口、cpu、地址等参数
def set_device():
    """
    POST接收到的数据格式为：{"para_name1": value, "para_name2": value}
    返回的是{"status": True or False}
    GET接收返回的是当前的设备参数，数据格式同上，为全部参数
    """
    if request.method == "GET":
        return jsonify(communicator.get_hardware_parameter(device_name="FanDriver")), 200
    else:
        status = communicator.update_hardware_parameter(device_name="FanDriver", para_dict=request.json)
        return jsonify({"status": status}), 200


@control.route("/checkdata", methods=["GET"])
def check_data():
    """
    检查数采是否正常
    返回{"status": True or False}
    """
<<<<<<< HEAD
    pass


@control.route("/setdevice", methods=["GET", "POST"])
# 对设备参数进行设置，修改设备名称，D轴电感、Q轴电感等参数
def set_device():
    """
    POST接收到的数据格式为：{"device_name": "fan1", "para_name": "D_coil", "value": 0.1}
    返回的是{"status": True or False}
    GET接收返回的是当前的设备参数，数据格式同上，为全部参数
    """
    pass
=======
    return jsonify({"status": communicator.check_thread_alive()}), 200
>>>>>>> 2af0e0f2a1be68e0adac5e3c1623b72f595c9ec1
