from . import control
from core.communication import communicator
from flask import request, jsonify
from core.database import outputdb
from application.utils import cn_translate


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
        if communicator.is_connected("TestDevice"):
            return jsonify({"status": False, "error": "请先关闭所有设备连接"}), 400
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
# 对风机及其通信接口进行设置，修改端口、cpu、地址等参数
def set_device():
    """
    POST接收到的数据格式为：{"para_name1": value, "para_name2": value}
    返回的是{"status": True or False}
    GET接收返回的是当前的设备参数，数据格式同上，为全部参数
    """
    # TODO:获取设备协议或者硬件配置
    if request.method == "GET":
        get_name = request.args.get("config_item", None)
        if get_name == "normal":
            return jsonify(communicator.get_hardware_parameter(device_name="FanDriver")[get_name]), 200
        elif get_name == "config":
            return communicator.find_driver("FanDriver").export_config(), 200
    elif request.method == "POST":
        # 修改端口，cpu等
        if communicator.is_connected("FanDriver"):
            return jsonify({"status": False, "error": "请先关闭所有设备连接"}), 400
        status = communicator.update_hardware_parameter(device_name="FanDriver", para_dict=request.json)
        return jsonify({"status": status}), 200
    else:
        # PUT，将设备协议的配置应用
        driver_name = request.form.get("driver_name")
        config = request.form.get("config")
        driver = communicator.find_driver(driver_name)
        driver.load_config(config)
        return jsonify({"status": True}), 200


@control.route("/deviceset", methods=["GET", "POST"])
# 对风机、测试设备及其通信接口进行设置，修改端口、cpu、地址等参数,以及对协议进行设置或读取
def set():
    """
    POST接收到的数据格式为：{"para_name1": value, "para_name2": value}
    返回的是{"status": True or False}
    GET接收返回的是当前的设备参数，数据格式同上，为全部参数
    """
    # TODO:获取设备协议或者硬件配置
    if request.method == "GET":
        get_name = request.args.get("config_item", None)
        driver_name = request.args.get("driver_name", None)
        if get_name == "normal":
            return jsonify(communicator.get_hardware_parameter(device_name=driver_name)[get_name]), 200
        elif get_name == "config":
            return communicator.find_driver(driver_name).export_config(), 200
    elif request.method == "POST":
        # 修改端口，cpu等
        driver_name = request.form.get("driver_name", None)
        if communicator.is_connected(driver_name):
            return jsonify({"status": False, "error": "请先关闭所有设备连接"}), 400
        status = communicator.update_hardware_parameter(device_name=driver_name, para_dict=request.json)
        return jsonify({"status": status}), 200
    else:
        # PUT，将设备协议的配置应用
        driver_name = request.form.get("driver_name")
        config = request.form.get("config")
        driver = communicator.find_driver(driver_name)
        driver.load_config(config)
        # 更新通讯模块的参数匹配
        communicator.update_map()
        return jsonify({"status": True}), 200


@control.route("config/apply", methods=["GET", "POST"])
def config_apply():
    """
    配置的应用，应用当前配置，GET为读取配置，POST为保存配置，PUT为加载配置
    """
    # 这里显示的是配置的细节
    if request.method == "GET":
        driver_name = request.args.get("driver_name", None)
        driver = communicator.find_driver("driver_name")
        driver_config = driver.export_config()
        # 将当前具有的所有配置返回,也可以只显示配置名字和ID
        # 这里只显示配置名字和ID
        return jsonify({driver_config}), 200
    elif request.method == "POST":
        driver_name = request.form.get("driver_name")
        driver = communicator.find_driver("driver_name")
        config = request.form.get("config")
        # 这里具体如何实现需要根据驱动来实现
        driver.load_config(config)


@control.route("config/save", methods=["GET", "POST", "PUT", "DELETE"])
def config_save():
    """
    配置的保存、加载等，读取当前具有的所有配置，保存当前配置，GET为读取配置，POST为保存配置，PUT为加载配置
    """
    # TODO:没有完全完成，需要测试
    if request.method == "GET":
        driver_name = request.args.get("driver_name", None)
        driver = communicator.find_driver("driver_name")
        outputdb.change_current_table(driver_name)
        driver_config = outputdb.select_data()
        # 将当前具有的所有配置返回,也可以只显示配置名字和ID
        # 这里只显示配置名字和ID
        return jsonify({driver_config}), 200
    elif request.method == "POST":
        # POST方法，保存当前设备配置
        driver_name = request.form.get("driver_name")
        config_name = request.form.get("config_name")
        driver = communicator.find_driver("driver_name")
        config_dict = driver.export_config()
        config_dict.update({"配置命名": config_name})
        # 将配置文件保存到数据库中
        config_column = config_to_columns(config_dict)
        outputdb.change_current_table(driver_name, config_column)
        outputdb.insert_data([config_dict])

        # 将配置文件保存到数据库中
        return jsonify({"status": True}), 200
    elif request.method == "PUT":
        driver_name = request.form.get("driver_name")
        config_id = request.form.get("config_id")
        outputdb.change_current_table(driver_name)
        driver_config = outputdb.select_data(ids_input=[config_id])
        if len(driver_config) != 1:
            return jsonify({"err": "查询错误"}), 400
        driver = communicator.find_driver("driver_name")
        driver.load_config(driver_config[0])
        return jsonify({"status": True}), 200
    else:
        # 删除配置
        driver_name = request.form.get("driver_name")
        config_id = request.form.get("config_id")
        outputdb.change_current_table(driver_name)
        outputdb.delete_data_by_ids(ids_input=[config_id])
        return jsonify({"status": True}), 200


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
    获取参数名称,返回的是设备名为key的参数表
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


@control.route("/custom_column", methods=["GET", "POST", "PUT", "DELETE"])
def custom_column():
    # TODO:用户自定义的参数计算
    if request.method == "GET":
        # 处理数据插入
        return jsonify(communicator.custom_calculate_map), 200
    elif request.method == "POST":
        # 处理数据修改
        datasstr: str = request.form.get("data")
        communicator.add_custom_column([datasstr])
    elif request.method == "PUT":
        datasstr: str = request.form.get("data")
        communicator.add_custom_column([datasstr])
    else:
        column_name = request.form.get("name")
        communicator.del_custom_column(column_name)


def config_to_columns(config: dict[str, any]) -> dict[str, str]:
    """
    将配置文件转换为数据库的列名
    """
    columns = {"ID": "INT AUTO_INCREMENT PRIMARY KEY"}
    for key, _ in config.items():
        columns[key] = "VARCHAR(255)"
    return columns
