from flask import Flask, render_template, url_for, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from core.communication import communicator
from core.auto_collection import auto_collector
import threading

app = Flask(__name__)
CORS(app, supports_credentials=True)
socketio = SocketIO(app)

communicator.connect()
communicator.start_read_all()

thread = None
thread_running = threading.Event()


@app.route("/")
def index():
    # 旧版页面
    pass


##############################设备设置############################


@app.route("/device", methods=["GET", "POST"])
# 对设备参数进行设置，修改设备名称，D轴电感、Q轴电感等参数
def set_device():
    """
    POST接收到的数据格式为：{"device_name": "fan1", "para_name": "D_coil", "value": 0.1}
    返回的是{"status": True or False}
    GET接收返回的是当前的设备参数，数据格式同上，为全部参数
    """
    pass


##############################数据采集############################


@socketio.on("connect")
# 连接对应设备，并开始获取数据
def connect():
    """
    返回的数据格式为{"status": True or False}
    """
    communicator.connect()
    print("Client connected")


@socketio.on("disconnect")
# 和对应的设备断连
def disconnect():
    """
    返回的数据格式为{"status": True or False}
    """
    pass


@app.route("datacollect/data", methods=["GET"])
@socketio.on("connect")
def get_data():
    """
    返回的数据格式为字典，key:value形式
    """
    return jsonify(communicator.read()), 200


@app.route("datacollect/para", methods=["GET", "POST"])
# 读取控制参数,修改控制参数
def get_para():
    """
    GET返回的数据格式为字典，key:value形式
    POST接收的数据格式为{"para_name": value}
    """
    return jsonify(communicator.read()), 200


##############################自动数采############################
@app.route("autocollect/csvparameter", methods=["POST"])
# 上传设备数据采集相关的csv文件
def upload_csv():
    """
    接收文件，返回需要自动采集的数据条数
    """
    pass


@app.route("autocollect/control", methods=["POST"])
# 自动数采的控制，包括启动、停止、暂停、停止、继续
def auto_collect_control():
    """
    接收"signal": "start", "stop", "pause", "continue"
    返回{"status": "start", "stop", "pause", "continue", "complete":True or False}
    """
    pass


@app.route("autocollect/view", methods=["GET"])
# 查看当前的数采进度
def get_current_progress():
    """
    返回{"current_data": current_data, "current_para":{"para1":value},"complete": False}
    """
    pass


###############################数据库操作############################


@app.route("/dbapi/show", methods=["GET", "POST", "PUT", "DELETE"])
# 数据库的展示操作，数据的获取，增删改查
def sqldb():
    pass


@app.route("/dbapi/export", methods=["POST"])
# 数据导出接口，根据发送的测试人员等信息导出数据，返回csv文件，由客户指定导出目录进行保存
def sqldb():
    pass
