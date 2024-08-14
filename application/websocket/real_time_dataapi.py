import time
from flask_socketio import SocketIO
from flask import Flask
import random
from flask import request, jsonify
from core.communication import communicator
import threading
from . import socketio_http
from core.communication.exception_handling import BREAKDOWNMAP

thread = None
thread_running = threading.Event()


def handle_socketio_events(socketio: SocketIO):

    @socketio_http.route("/connect_device", methods=["POST"])
    # 连接对应设备，并开始获取数据
    def device_connect():
        """
        返回的数据格式为{"status": True or False}
        """
        global thread
        command = request.form.get("command")
        device_name = request.form.get("device_name")
        if command == "connect":
            if communicator.connect(device_name):
                if communicator.start_read_all(device_name):
                    if thread == None:
                        thread_running.clear()
                        thread = socketio.start_background_task(target=get_data)
                    return jsonify({"err": ""}), 200
                else:
                    return jsonify({"err": "启动读数据失败"}), 400
            else:
                return jsonify({"err": "连接设备失败"}), 400
        elif command == "disconnect":
            if communicator.is_read_all(device_name):
                if communicator.stop_read_all(device_name):
                    if communicator.disconnect(device_name):
                        if communicator.read_all_driver_number() == 0:
                            # 如果此时已经没有设备在读取数据，就清空读数据线程
                            thread_running.set()
                            thread = None
                        return jsonify({"err": ""}), 200
                    else:
                        return jsonify({"err": "断连失败"}), 400
                else:
                    return jsonify({"err": "停止读数据失败"}), 400
            else:
                return jsonify({"err": "设备未读数据"}), 400
        else:
            return jsonify({"err": "未知命令"}), 400

    @socketio.on("current_data")
    def get_data():
        """
        从数据采集模块获取数据，
        """
        while True:
            if thread_running.is_set():
                thread_running.clear()
                break
            socketio.sleep(0.05)
            data = communicator.read()
            para = communicator.get_curr_para()
            total = {**data, **para}
            if "故障" in total.keys():
                breakdown_list = breakdown_replace(total["故障"])
                total["故障"] = breakdown_list
            # for key in list(total.keys()).copy():
            #     # if key in TABLE_TRANSLATE.keys():
            #     total[cn_translate(key)] = total.pop(key)
            socketio.emit("data_from_device", total)


# def breakdown_replace(breakdown: list[str]) -> list[str]:
#     """
#     将故障代码翻译为中文
#     """
#     result = []
#     for item in breakdown:
#         if item in BREAKDOWNMAP.keys():
#             result.append(BREAKDOWNMAP[item])
#         else:
#             result.append(item)
#     return result


def breakdown_replace(breakdown: int) -> list[str]:
    """
    将故障代码翻译为中文
    """
    if breakdown in BREAKDOWNMAP.keys():
        return BREAKDOWNMAP[breakdown]
    else:
        return breakdown


# 导出函数以便在主应用中调用
def init_socketio_events(app: Flask):
    socketio = app.extensions["socketio"]
    handle_socketio_events(socketio)
