from flask_socketio import SocketIO
from flask import Flask
import random


def handle_socketio_events(socketio: SocketIO):

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
