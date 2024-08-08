import time
from flask_socketio import SocketIO
from flask import Flask
import random
from core.communication import communicator
import threading
from application.utils import cn_translate, TABLE_TRANSLATE

thread = None
thread_running = threading.Event()


def handle_socketio_events(socketio: SocketIO):

    @socketio.on("connect")
    # socketio建立连接
    def connect():
        """
        返回的数据格式为{"status": True or False}
        """
        if communicator.is_read_all():
            socketio.emit("connection", {"status": True})
            print("Readall is running")
        else:
            socketio.emit("connection", {"status": False})
            print("Readall is shutdown")
        print("Client connected")

    @socketio.on("disconnect")
    # socketio断开连接
    def disconnect():
        """
        返回的数据格式为{"status": True or False}
        """
        pass
        # TODO:在网络不稳定的时候，有时候会导致socket突然断掉，这个最好是先不加
        # # thread_running.set()
        # # if communicator.is_read_all():
        #     # communicator.stop_read_all()
        #     # communicator.disconnect()

    @socketio.on("connect_device")
    # 连接对应设备，并开始获取数据
    def device_connect():
        """
        返回的数据格式为{"status": True or False}
        """
        if communicator.connect():
            if communicator.start_read_all():
                thread_running.clear()
                thread = socketio.start_background_task(target=get_data)
                socketio.emit("connection", {"status": True})
            else:
                socketio.emit("connection", {"status": False})
        else:
            socketio.emit("connection", {"status": False})

    @socketio.on("disconnect_device")
    # 断开设备连接
    def device_disconnect():
        """
        返回的数据格式为{"status": True or False}
        """
        thread_running.set()
        if communicator.is_read_all():
            communicator.stop_read_all()
            communicator.disconnect()
        socketio.emit("connection", {"status": False})
        time.sleep(0.1)
        socketio.emit("data_from_device", {})

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
            for key in list(total.keys()).copy():
                # if key in TABLE_TRANSLATE.keys():
                total[cn_translate(key)] = total.pop(key)
            socketio.emit("data_from_device", total)


# 导出函数以便在主应用中调用
def init_socketio_events(app: Flask):
    socketio = app.extensions["socketio"]
    handle_socketio_events(socketio)
