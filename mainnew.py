from flask import Flask, render_template, url_for, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from core.communication import communicator
from core.auto_collection import auto_collector
import threading

from application.auto_collection import autocollect
from application.database import db
from application.device_control import control
from application.websocket.real_time_dataapi import init_socketio_events

app = Flask(__name__)
socketio = SocketIO(app)
CORS(app, supports_credentials=True)

app.register_blueprint(autocollect, url_prefix="/collect")
app.register_blueprint(db, url_prefix="/db")
app.register_blueprint(control, url_prefix="/control")
init_socketio_events(app)


@app.route("/")
def index():
    # 旧版页面
    return render_template("index.html")


# 路由到第二个index.html
@app.route("/second")
def index1():
    return render_template("index_database.html")


def get_apis():
    # 获取当前所有api
    print(app.url_map)


if __name__ == "__main__":
    socketio.run(app, debug=True, host="127.0.0.1", port=5000)


# 考虑浏览器页面意外关闭，也就是disconnect的时候，如何处理，如果有正在进行的自动采集，那么需要暂停自动采集
