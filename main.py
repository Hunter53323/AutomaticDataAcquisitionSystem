from flask import Flask, render_template, url_for, request, jsonify
from flask_socketio import SocketIO
import random
import threading
from core.communication.drivers.ControlDriver import Driver
import time

app = Flask(__name__)
socketio = SocketIO(app)

thread = None
thread_running = threading.Event()

client = Driver([("电机驱动", "COM10")])


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
        return jsonify({"status": "search", "current_data": current_data, "complete": False}), 200
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


def get_data():
    """
    从数据采集模块获取数据，
    """
    while thread_running.is_set():
        socketio.sleep(0.05)  # 50毫秒
        status, speed = client.read_from_parameter("电机驱动", "实际转速")
        if status == False:
            speed = "error"
        # status, faultinformation = client.read_from_parameter("电机驱动", "故障信息")
        # if status == False:
        #     faultinformation = "error"
        # 这一块可能需要考虑多线程
        speed = [random.random()]
        faultinformation = [random.randint(0, 1)]
        socketio.emit(
            "data_from_device",
            {
                "currentrotationalspeed": speed[0],
                "faultinformation": faultinformation[0],
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
    client.connect_all_device()
    socketio.emit("connection", {"status": client.connect_all_device()})
    # thread = threading.Thread(target=random_data, args=(client,))
    # thread.start()


@socketio.on("disconnect_device")
def disconnect_device():
    client.close()
    socketio.emit("connection", {"status": False})


def random_data(client: Driver):
    i = 0
    while i < 1000:
        i += 1
        socketio.sleep(0.01)
        client.write_from_parameter("电机驱动", "实际转速", random.randint(0, 100))
        client.write_from_parameter("电机驱动", "故障信息", random.randint(0, 2))


if __name__ == "__main__":
    socketio.run(app, debug=True, host="127.0.0.1", port=5000)
