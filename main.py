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
    return render_template("index.html")


@socketio.on("connect")
def connected():
    print("Client connected")


@socketio.on("disconnect")
def disconnected():
    print("Client disconnected")


@app.route("/upload", methods=["POST"])
def upload_csv():
    """处理获得的csv文件，返回需要自动采集的数据"""
    if "file" not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400
    if file:
        # 在这里处理文件，例如保存文件或读取内容
        # file.save(os.path.join('uploads', file.filename))  # 保存文件
        csv_data = file.read().decode("utf-8")
        line_count = csv_data.count("\n")  # 行数等于换行符数量加1
        # 处理CSV数据，例如解析、保存到数据库等
        # ...
        return jsonify({"line_count": line_count}), 200

    return jsonify({"message": "Unknown error"}), 500


@app.route("/collect", methods=["POST"])
def collect_data():
    """处理采集数据的开始、停止等请求"""
    signal = request.form.get("signal")
    if signal == "start":
        # 启动数据采集，（所有前期基本参数已经设置好）
        return jsonify({"status": "start", "current_data": 0, "complete": False}), 200
    elif signal == "search":
        # 查询当前数据采集的状态，返回当前正在采集第几条数据
        current_data = 1
        return (
            jsonify({"status": "search", "current_data": current_data, "complete": False}),
            200,
        )
    elif signal == "pause":
        # 暂停数采
        return jsonify({"status": "pause"}), 200
    elif signal == "continue":
        # 恢复数采
        return jsonify({"status": "continue"}), 200
    elif signal == "stop":
        # 停止数采，是终止，无法再次启动
        return jsonify({"status": "stop"}), 200
    else:
        return jsonify({"status": "error"}), 400


@app.route("/data", methods=["GET"])
def get_data():
    # 不止要读取数据，还要读取控制参数
    return jsonify(communicator.read()), 200


# def get_data():
#     """
#     从数据采集模块获取数据，
#     """
#     while thread_running.is_set():
#         socketio.sleep(0.05)  # 50毫秒
#         status, speed = client.read_from_parameter("电机驱动", "实际转速")
#         if status == False:
#             speed = "error"
#         # status, faultinformation = client.read_from_parameter("电机驱动", "故障信息")
#         # if status == False:
#         #     faultinformation = "error"
#         # 这一块可能需要考虑多线程
#         speed = [random.random()]
#         faultinformation = [random.randint(0, 1)]
#         socketio.emit(
#             "data_from_device",
#             {
#                 "currentrotationalspeed": speed[0],
#                 "faultinformation": faultinformation[0],
#                 "setrotationalspeed": random.randint(0, 100),
#                 "targetrotationalspeed": random.randint(0, 100),
#                 "dcbusvoltage": random.randint(0, 100),
#                 "uphasecurrent": random.randint(0, 100),
#                 "power": random.randint(0, 100),
#                 "dissipativeresistance": random.randint(0, 100),
#                 "daxieinductor": random.randint(0, 100),
#                 "qaxieinductor": random.randint(0, 100),
#                 "reverseemfconstant": random.randint(0, 100),
#                 "polaritylog": random.randint(0, 100),
#                 "motorinputpower": random.randint(0, 100),
#                 "torque": random.randint(0, 100),
#                 "motoroutputpower": random.randint(0, 100),
#                 "addload": random.randint(0, 100),
#                 "speedcompensationcoefficient": random.randint(0, 100),
#                 "currentbandwidth": random.randint(0, 100),
#                 "observercompensationcoefficient": random.randint(0, 100),
#                 "load": random.randint(0, 100),
#                 "speed": random.randint(0, 100),
#             },
#         )


@app.route("/para", methods=["GET"])
def get_para():
    return jsonify(communicator.get_curr_para()), 200


@app.route("/para", methods=["POST"])
def set_para():
    para_to_set_dict = request.form.get("paraToSet")
    try:
        communicator.write()
        return jsonify({"result": "success"}), 200
    except Exception():
        return jsonify({"result": "fault", "msg": "Fault Message"}), 400


def get_data():
    """
    从数据采集模块获取数据，
    """
    while thread_running.is_set():
        socketio.sleep(0.05)  # 50ms
        socketio.emit("data_from_device", communicator.read())


@socketio.on("start_data")
def start_data():
    global thread
    if not thread_running.is_set():
        thread_running.set()
        thread = socketio.start_background_task(get_data)


@socketio.on("stop_data")
def stop_data():
    thread_running.clear()


@socketio.on("connect_device")
def connect_device():
    communicator.connect()
    socketio.emit("connection", {"status": communicator.connect()})
    # thread = threading.Thread(target=random_data, args=(client,))
    # thread.start()


@socketio.on("disconnect_device")
def disconnect_device():
    communicator.disconnect()
    socketio.emit("connection", {"status": False})


if __name__ == "__main__":
    socketio.run(app, debug=True, host="127.0.0.1", port=5000)
