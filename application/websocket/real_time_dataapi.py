import time
from flask_socketio import SocketIO
from flask import Flask
import random
from flask import request, jsonify
from core.communication import communicator
import threading
from . import socketio_http
from core.auto_collection import auto_collector

# from core.communication.exception_handling import BREAKDOWNMAP
from core.warningmessage import emailsender

thread = None
thread_running = threading.Event()
send_data_thread = None
send_data_thread_running = threading.Event()


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

    def get_data():
        """
        从数据采集模块获取数据，
        """
        while True:
            global thread
            if communicator.check_error():
                communicator.close_all_device()
                communicator.stop_read_all()
                communicator.disconnect()
                thread_running.set()
                thread = None
                emailsender.send_email("读写故障", "数据采集模块出现读写故障，请检查")
            if thread_running.is_set():
                thread_running.clear()
                break
            socketio.sleep(0.05)
            data = communicator.read()
            para = communicator.get_curr_para()
            total = {**data, **para}
            # if "故障" in total.keys():
            #     breakdown_list = breakdown_replace(total["故障"])
            #     total["故障"] = breakdown_list
            socketio.emit("data_from_device", total)

    def send_data():
        while True:
            socketio.sleep(0.2)
            if send_data_thread_running.is_set():
                send_data_thread_running.clear()
                break
            success, fail, remaining, status = auto_collector.get_current_progress()
            send_dict = {"auto_collect_status": {"success": success, "fail": fail, "remaining": remaining, "status": status}}

            for driver in communicator.drivers:
                send_dict[driver.device_name] = driver.get_device_state()
            socketio.emit("device_status", send_dict)
            # print("send data")

    @socketio.on("connect")
    def connect():
        global send_data_thread
        if send_data_thread == None:
            send_data_thread_running.clear()
            send_data_thread = socketio.start_background_task(target=send_data)

    @socketio.on("disconnect")
    def disconnect():
        global send_data_thread
        send_data_thread_running.set()
        send_data_thread = None


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


# def breakdown_replace(breakdown: int) -> list[str]:
#     """
#     将故障代码翻译为中文
#     """
#     if breakdown in BREAKDOWNMAP.keys():
#         return BREAKDOWNMAP[breakdown]
#     else:
#         return breakdown


# 导出函数以便在主应用中调用
def init_socketio_events(app: Flask):
    socketio = app.extensions["socketio"]
    handle_socketio_events(socketio)
