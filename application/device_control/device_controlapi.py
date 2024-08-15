from . import control
from core.communication import communicator
from flask import request, jsonify
from core.database import outputdb
import json


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
            status = test_device.write({"测试设备控制命令": "启动"})
        elif command == "stop":
            status = test_device.write({"测试设备控制命令": "停止"})
        elif command == "P_mode":
            status = test_device.write({"测试设备控制命令": "P_mode"})
        elif command == "N_mode":
            status = test_device.write({"测试设备控制命令": "N_mode"})
        elif command == "N1_mode":
            status = test_device.write({"测试设备控制命令": "N1_mode"})
        else:
            status = False

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
                    "控制命令": "启动",
                }
            )
        elif command == "stop":
            status = fan.write({"控制命令": "停止"})
        elif command == "clear_breakdown":
            status = fan.handle_breakdown(1)
        else:
            status = False

        return jsonify({"status": status}), 200


@control.route("/deviceset", methods=["GET", "POST", "PUT"])
# 对风机、测试设备及其通信接口进行设置，修改端口、cpu、地址等参数,以及对协议进行设置或读取
def set():
    """
    POST接收到的数据格式为：{"para_name1": value, "para_name2": value}
    返回的是{"status": True or False}
    GET接收返回的是当前的设备参数，数据格式同上，为全部参数
    """
    # TODO:获取设备协议或者硬件配置
    if request.method == "GET":
        """
        config为协议配置，normal为基础配置
        示例：curl http://127.0.0.1:5000/control/deviceset?config_item=config&driver_name=FanDriver
        """
        get_name = request.args.get("config_item", None)
        driver_name = request.args.get("driver_name", None)
        if get_name == "normal":
            return jsonify(communicator.get_hardware_parameter(device_name=driver_name)), 200
        elif get_name == "config":
            # 这里显示的是导出的协议配置明细
            return jsonify(communicator.find_driver(driver_name).export_config()), 200
    elif request.method == "POST":
        # POST为修改端口，cpu等基础配置
        """
        示例：curl -X POST http://127.0.0.1:5000/control/deviceset?&driver_name=FanDriver \
        -H "Content-Type: application/json" \
        -d '{"cpu": "M4", "port": "COM1"}'
        """
        driver_name = request.args.get("driver_name", None)
        if communicator.is_connected(driver_name):
            return jsonify({"status": False, "error": "请先关闭所有设备连接"}), 400
        status = communicator.update_hardware_parameter(device_name=driver_name, para_dict=request.json)
        return jsonify({"status": status}), 200
    else:
        # PUT为加载设备协议配置
        """
        示例：(GET获得的东西原封不动扔回来就行)
        curl -X PUT http://127.0.0.1:5000/control/deviceset?&driver_name=FanDriver \
        -H "Content-Type: application/json" \
        -d '
        {"ack_control_f": "{\"header\": \"5a\", \"tail\": \"a5\", \"cmd\": \"01\", \"addr\": \"ff\", \"data\": [{\"type\": \"bit8\", \"index\": 1, \"name\": \"send_result\", \"size\": 1, \"formula\": \"\", \"inv_formula\": \"\", \"raw_data\": 0, \"real_data\": 0}]}",
        "ack_query_f": "{\"header\": \"5a\", \"tail\": \"a5\", \"cmd\": \"02\", \"addr\": \"ff\", \"data\": [{\"type\": \"int16\", \"index\": 1, \"name\": \"\\u76ee\\u6807\\u8f6c\\u901f\", \"size\": 2, \"formula\": \"real_data=raw_data* 25 * 60 / 32768\", \"inv_formula\": \"raw_data=8192*real_data/375\", \"raw_data\": 0, \"real_data\": 0.0}, {\"type\": \"int16\", \"index\": 2, \"name\": \"\\u5b9e\\u9645\\u8f6c\\u901f\", \"size\": 2, \"formula\": \"real_data=raw_data* 25 * 60 / 32768\", \"inv_formula\": \"raw_data=8192*real_data/375\", \"raw_data\": 0, \"real_data\": 0.0}, {\"type\": \"int16\", \"index\": 3, \"name\": \"\\u76f4\\u6d41\\u6bcd\\u7ebf\\u7535\\u538b\", \"size\": 2, \"formula\": \"real_data=raw_data* 380 / 32768\", \"inv_formula\": \"raw_data=8192*real_data/95\", \"raw_data\": 0, \"real_data\": 0.0}, {\"type\": \"int16\", \"index\": 4, \"name\": \"U\\u76f8\\u7535\\u6d41\\u6709\\u6548\\u503c\", \"size\": 2, \"formula\": \"real_data=raw_data* 2 / 32768 / 1\", \"inv_formula\": \"raw_data=16384*real_data\", \"raw_data\": 0, \"real_data\": 0.0}, {\"type\": \"int16\", \"index\": 5, \"name\": \"\\u529f\\u7387\", \"size\": 2, \"formula\": \"real_data=raw_data* 2 * 380 * 3 / 2 / 32768 / 1\", \"inv_formula\": \"raw_data=8192*real_data/285\", \"raw_data\": 0, \"real_data\": 0.0}, {\"type\": \"bit16\", \"index\": 6, \"name\": \"\\u6545\\u969c\", \"size\": 2, \"formula\": \"\", \"inv_formula\": \"\", \"raw_data\": 0, \"real_data\": 0}]}",
        "control_f": "{\"header\": \"a5\", \"tail\": \"5a\", \"cmd\": \"01\", \"addr\": \"01\", \"data\": [{\"type\": \"bit8\", \"index\": 1, \"name\": \"\\u63a7\\u5236\\u547d\\u4ee4\", \"size\": 1, \"formula\": \"real_data=raw_data\", \"inv_formula\": \"\", \"raw_data\": 0, \"real_data\": 0}, {\"type\": \"int16\", \"index\": 2, \"name\": \"\\u8bbe\\u5b9a\\u8f6c\\u901f\", \"size\": 2, \"formula\": \"real_data=raw_data\", \"inv_formula\": \"raw_data=real_data\", \"raw_data\": 0, \"real_data\": 0}, {\"type\": \"int16\", \"index\": 3, \"name\": \"\\u901f\\u5ea6\\u73af\\u8865\\u507f\\u7cfb\\u6570\", \"size\": 2, \"formula\": \"real_data=raw_data*10\", \"inv_formula\": \"raw_data=real_data/10\", \"raw_data\": 0, \"real_data\": 0}, {\"type\": \"int16\", \"index\": 4, \"name\": \"\\u7535\\u6d41\\u73af\\u5e26\\u5bbd\", \"size\": 2, \"formula\": \"real_data=raw_data\", \"inv_formula\": \"raw_data=real_data\", \"raw_data\": 0, \"real_data\": 0}, {\"type\": \"int16\", \"index\": 5, \"name\": \"\\u89c2\\u6d4b\\u5668\\u8865\\u507f\\u7cfb\\u6570\", \"size\": 2, \"formula\": \"real_data=raw_data*100\", \"inv_formula\": \"raw_data=real_data/100\", \"raw_data\": 0, \"real_data\": 0}]}",
        "query_f": "{\"header\": \"a5\", \"tail\": \"5a\", \"cmd\": \"02\", \"addr\": \"01\", \"data\": []}"
        }'


        curl -X PUT http://127.0.0.1:5000/control/deviceset?&driver_name=TestDevice \
        -H "Content-Type: application/json" \
        -d '
        {"rev_f": "{\"tid\": \"0000\", \"pid\": \"0000\", \"length\": 13, \"uid\": \"01\", \"fc\": \"03\", \"data\": [{\"type\": \"float\", \"index\": 1, \"name\": \"\\u8f93\\u5165\\u529f\\u7387\", \"size\": 4, \"formula\": \"real_data=raw_data\", \"inv_formula\": \"raw_data=real_data\", \"raw_data\": 0, \"real_data\": 0}, {\"type\": \"float\", \"index\": 2, \"name\": \"\\u626d\\u77e9\", \"size\": 4, \"formula\": \"real_data=raw_data\", \"inv_formula\": \"raw_data=real_data\", \"raw_data\": 0, \"real_data\": 0}, {\"type\": \"float\", \"index\": 3, \"name\": \"\\u8f93\\u51fa\\u529f\\u7387\", \"size\": 4, \"formula\": \"real_data=raw_data\", \"inv_formula\": \"raw_data=real_data\", \"raw_data\": 0, \"real_data\": 0}]}"
        }'
        """
        # PUT，将设备协议的配置应用
        driver_name = request.args.get("driver_name", None)
        if communicator.is_connected(driver_name):
            return jsonify({"status": False, "error": "请先关闭所有设备连接"}), 400
        config = request.json
        driver = communicator.find_driver(driver_name)
        if driver.load_config(config):
            # 更新通讯模块的参数匹配
            status, err = communicator.update_map()
            return jsonify({"status": status, "error": err}), 200
        else:
            return jsonify({"status": False}), 400


@control.route("/configsave", methods=["GET", "POST", "PUT", "DELETE"])
def config_save():
    """
    配置的保存、加载等，读取当前具有的所有配置，保存当前配置，GET为读取配置，POST为保存配置，PUT为加载配置
    """
    # TODO:没有完全完成，需要测试
    driver_name = request.args.get("driver_name", None)
    driver = communicator.find_driver(driver_name)
    config_dict = driver.export_config()
    config_dict.update({"配置命名": "config_name"})
    config_column = config_to_columns(config_dict)
    if request.method == "GET":
        """
        curl http://127.0.0.1:5000/control/configsave?driver_name=FanDriver
        """
        if not outputdb.change_current_table(driver_name):
            outputdb.change_current_table(driver_name, config_column)
        driver_config = outputdb.select_data(columns=["ID", "配置命名"])
        # 这里只显示配置名字和ID
        return jsonify({"name": ["ID", "配置命名"], "value": driver_config}), 200
    elif request.method == "POST":
        """
        curl -X POST http://127.0.0.1:5000/control/configsave?driver_name=FanDriver&config_name=测试配置
        """
        # POST方法，保存当前设备配置
        config_name = request.args.get("config_name", None)
        for key, value in config_dict.items():
            config_dict[key] = json.dumps(config_dict[key])
        config_dict.update({"配置命名": config_name})
        outputdb.change_current_table(driver_name, config_column)
        driver_config = outputdb.select_data(columns=["ID", "配置命名"])
        for config in driver_config:
            if config[1] == config_name:
                return jsonify({"status": False, "err": "配置名重复"}), 400
        outputdb.insert_data([config_dict])

        # 将配置文件保存到数据库中
        return jsonify({"status": True, "error": ""}), 200
    elif request.method == "PUT":
        """
        curl -X PUT http://127.0.0.1:5000/control/configsave?driver_name=FanDriver&config_id=1
        """
        # PUT方法，加载配置
        config_id = request.args.get("config_id")
        if not outputdb.change_current_table(driver_name):
            outputdb.change_current_table(driver_name, config_column)
        driver_config = outputdb.select_data(ids_input=[int(config_id)])
        if len(driver_config) != 1:
            return jsonify({"err": "查询错误"}), 400
        load_config_dict = {}
        count = 0
        for key in config_column.keys():
            if key == "ID" or key == "配置命名":
                count += 1
                continue
            load_config_dict[key] = json.loads(driver_config[0][count])
        driver.load_config(load_config_dict)
        return jsonify({"status": True}), 200
    else:
        # 删除配置
        """
        curl -X DELETE http://127.0.0.1:5000/control/configsave?driver_name=FanDriver&config_id=1
        """
        config_id = request.args.get("config_id")
        if not outputdb.change_current_table(driver_name):
            outputdb.change_current_table(driver_name, config_column)
        if outputdb.delete_data_by_ids(ids_input=[int(config_id)]):
            outputdb.rearrange_ids()
            return jsonify({"status": True}), 200
        else:
            return jsonify({"status": False}), 400


@control.route("/checkdata", methods=["GET"])
def check_data():
    """
    检查数采是否正常
    返回{"status": True or False}
    """
    driver_name = request.args.get("driver_name")
    return jsonify({"status": communicator.check_thread_alive(driver_name)}), 200


@control.route("/parameters", methods=["GET"])
def get_parameters():
    """
    获取参数名称,返回的是设备名为key的参数表
    """
    paras = communicator.get_device_and_para()
    return jsonify(paras), 200


@control.route("/data", methods=["GET"])
def get_data():
    """
    获取数据名称，返回的是设备名为key的数据表，包括数据单位
    现在是不带单位的版本，带单位的需要改动一下底层，后续再做支持
    """
    paras = communicator.get_device_and_data()
    return jsonify(paras), 200


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
        """
        示例：curl -X POST http://127.0.0.1:5000/control/custom_column -d 'data=效率%3D输入功率/输出功率'
        %3D是=的url编码
        """
        datasstr: str = request.form.get("data")
        return jsonify(communicator.add_custom_column([datasstr])), 200
    elif request.method == "PUT":
        """
        示例：curl -X POST http://127.0.0.1:5000/control/custom_column -d 'data=效率%3D输入功率/输出功率'
        %3D是=的url编码
        """
        datasstr: str = request.form.get("data")
        return jsonify(communicator.add_custom_column([datasstr])), 200
    else:
        """
        示例：curl -X DELETE http://127.0.0.1:5000/control/custom_column -d 'name=效率'
        """
        column_name = request.form.get("name")
        return jsonify(communicator.del_custom_column(column_name)), 200


def config_to_columns(config: dict[str, any]) -> dict[str, str]:
    """
    将配置文件转换为数据库的列名
    """
    columns = {"ID": "INT AUTO_INCREMENT PRIMARY KEY"}
    for key, _ in config.items():
        columns[key] = "VARCHAR(2048)"
    return columns
