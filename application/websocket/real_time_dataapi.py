from flask_socketio import SocketIO
from flask import Flask
import random
<<<<<<< HEAD
=======
from core.communication import communicator
>>>>>>> 2af0e0f2a1be68e0adac5e3c1623b72f595c9ec1


def handle_socketio_events(socketio: SocketIO):

<<<<<<< HEAD
=======
    @socketio.on("connect")
    # 连接对应设备，并开始获取数据
    def connect():
        """
        返回的数据格式为{"status": True or False}
        """
        communicator.connect()
        communicator.start_read_all()
        print("Client connected")

    @socketio.on("disconnect")
    # 和对应的设备断连
    def disconnect():
        """
        返回的数据格式为{"status": True or False}
        """
        communicator.stop_read_all()
        communicator.disconnect()
        pass

>>>>>>> 2af0e0f2a1be68e0adac5e3c1623b72f595c9ec1
    @socketio.on("current_data")
    def get_data():
        """
        从数据采集模块获取数据，
        """
        socketio.emit(
            "data_from_device",
            {
                "currentrotationalspeed": random.randint(0, 100),
                "faultinformation": random.randint(0, 100),
                "setrotationalspeed": random.randint(0, 100),
                "targetrotationalspeed": random.randint(0, 100),
                "dcbusvoltage": random.randint(0, 100),
                "uphasecurrent": random.randint(0, 100),
                "power": random.randint(0, 100),
                "dissipativeresistance": random.randint(0, 100),
                "daxieinductor": random.randint(0, 100),
                "qaxieinductor": random.randint(0, 100),
                "reverseemfconstant": random.randint(0, 100),
                "polaritylog": random.randint(0, 100),
                "motorinputpower": random.randint(0, 100),
                "torque": random.randint(0, 100),
                "motoroutputpower": random.randint(0, 100),
                "addload": random.randint(0, 100),
                "speedcompensationcoefficient": random.randint(0, 100),
                "currentbandwidth": random.randint(0, 100),
                "observercompensationcoefficient": random.randint(0, 100),
                "load": random.randint(0, 100),
                "speed": random.randint(0, 100),
            },
        )


# 导出函数以便在主应用中调用
def init_socketio_events(app: Flask):
    socketio = app.extensions["socketio"]
    handle_socketio_events(socketio)
