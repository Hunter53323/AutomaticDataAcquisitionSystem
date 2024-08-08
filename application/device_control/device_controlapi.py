from . import control
from core.communication import communicator
from core.database import TABLE_TRANSLATE
from flask import request, jsonify


@control.route("/testdevice", methods=["GET", "POST"])
# 测试设备控制
def testdevice_control():
    """
    测试设备控制和状态获取
    """
    test_device = communicator.find_driver("TestDevice")
    if request.method == "GET":
        return jsonify(test_device.get_device_state()), 200
    if request.method == "POST":
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


@control.route("/fan", methods=["GET", "POST"])
# 风机控制
def fan_control():
    """
    接收"command": "start", "stop", "clear_breakdown"
    返回{"status": True or False}
    """
    fan = communicator.find_driver("FanDriver")
    if request.method == "GET":
        return jsonify(fan.get_device_state()), 200
    if request.method == "POST":
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
    return jsonify({"status": communicator.check_thread_alive()}), 200


@control.route("/parameters", methods=["GET"])
def get_parameters():
    """
    获取参数,返回的是设备名为key的参数表
    """
    en_paras = communicator.get_device_and_para()
    cn_paras = {}
    for key, value in en_paras.items():
        cn_paras[key] = [cn_translate(para) for para in value]
    return jsonify(cn_paras), 200


@control.route("/data", methods=["GET"])
def get_data():
    """
    获取数据名称，返回的是设备名为key的数据表，包括数据单位
    现在是不带单位的版本，带单位的需要改动一下底层，后续再做支持
    """
    en_paras = communicator.get_device_and_data()
    cn_paras = {}
    for key, value in en_paras.items():
        cn_paras[key] = [cn_translate(para) for para in value]
    return jsonify(cn_paras), 200


@control.route("/state", methods=["GET"])
def state():
    """
    获取设备当前的状态
    """
    state_dict = communicator.get_device_state()
    return jsonify(state_dict), 200


def cn_translate(en: str):
    """
    将英文参数名翻译为中文
    """
    return TABLE_TRANSLATE.get(en, en)
