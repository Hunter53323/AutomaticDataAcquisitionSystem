from io import StringIO
from . import autocollect
from flask import request, jsonify
import csv, time, threading
from werkzeug.datastructures import FileStorage
from core.auto_collection import auto_collector
from core.warningmessage import emailsender

autocollect_thread: threading.Thread = None


@autocollect.route("/csvupload", methods=["POST"])
# 上传设备数据采集相关的csv文件
def upload_csv():
    """
    接收文件，返回需要自动采集的数据条数
    """
    if "file" not in request.files:
        return jsonify({"message": "No file part"}), 400

    file: FileStorage = request.files["file"]

    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400
    if file:
        # 在这里处理文件，例如保存文件或读取内容
        # file.save(os.path.join('uploads', file.filename))  # 保存文件
        try:
            csv_data: str = file.read().decode("utf-8")
        except UnicodeDecodeError:
            return jsonify({"message": "文件编码错误,请使用utf-8格式的csv文件"}), 400
        line_count = csv_data.count("\n") - 1  # 行数等于换行符数量加1
        # 处理CSV数据，例如解析、保存到数据库等
        # ...
        file = StringIO(csv_data)
        reader = csv.DictReader(file)
        # csv_context 是一个字典列表，其中每个字典表示 CSV 文件中的一行
        csv_context = list(reader)

        for row in csv_context:
            if "ID" in row:
                del row["ID"]
            elif "\ufeffID" in row:
                del row["\ufeffID"]
            else:
                return jsonify({"message": "文件编码错误,请使用utf-8格式的csv文件"}), 400

        if auto_collector.init_para_pool_from_csv(csv_context):
            return jsonify({"message": "文件上传成功", "line_count": line_count}), 200
        else:
            return jsonify({"message": "文件上传失败"}), 400

    return jsonify({"message": "Unknown error"}), 500
    pass


@autocollect.route("/uploadparameter", methods=["POST"])
def upload_parameter():
    """
    上传设备用于数采的控制参数，返回上传的参数列表，控制参数的配置项最好可以从para_list中获取，因为可能自定义
    示例请求：curl -X POST http://127.0.0.1:5000/collect/uploadparameter \
    -H "Content-Type: application/json" \
    -d '{"parameters": {"负载量": [1, 2, 3, 4], "设定转速": [1, 2, 3, 4], "速度环补偿系数": [1, 2, 3, 4], "电流环带宽": [1, 2, 3, 4], "观测器补偿系数": [1, 2, 3, 4]}}'
    {"parameters": {"负载量": {"min":1,"max":10,"step":2}}}
    """
    para_dict = request.get_json().get("parameters")
    if not isinstance(para_dict, dict):
        return jsonify({"message": "参数格式错误"}), 400
    state, count = auto_collector.init_para_pool(para_dict)
    if state:
        return jsonify({"message": "参数上传成功", "line_count": count}), 200
    else:
        return jsonify({"message": "参数上传失败"}), 400


@autocollect.route("/control", methods=["POST"])
# 自动数采的控制，包括启动、停止、暂停、停止、继续
def auto_collect_control():
    """
    处理采集数据的开始、停止等请求
    接收"command": "start", "stop", "pause", "continue"
    返回{"status": "True", "error"}
    """
    command = request.form.get("command")
    global autocollect_thread
    if command == "start":
        # 启动数据采集，（所有前期基本参数已经设置好）
        status, autocollect_thread = auto_collector.start_auto_collect()
        return jsonify({"status": status}), 200
    elif command == "pause":
        # 暂停数采
        auto_collector.pause_auto_collect()
        return jsonify({"status": "True"}), 200
    elif command == "continue":
        # 恢复数采
        auto_collector.continue_auto_collect()
        return jsonify({"status": "True"}), 200
    elif command == "stop":
        # 停止数采，是终止，无法再次启动
        auto_collector.stop_auto_collect()
        autocollect_thread.join()
        if auto_collector.clear_para():
            return jsonify({"status": "True"}), 200
        else:
            return jsonify({"status": "error"}), 400
    else:
        return jsonify({"status": "error"}), 400


@autocollect.route("/view", methods=["GET"])
# 查看当前的数采进度
def get_current_progress():
    """
    返回{"success": int, "fail":int, "remaining":int, "complete": False}
    """
    success, fail, remaining, status = auto_collector.get_current_progress()
    return jsonify({"success": success, "fail": fail, "remaining": remaining, "complete": not status}), 200


@autocollect.route("/steady_state_determination", methods=["GET", "POST"])
def steady_state_determination():
    if request.method == "GET":
        # 获得当前的稳态判断逻辑
        return jsonify({"value": auto_collector.get_steady_state_determination()}), 200
    elif request.method == "POST":
        """
        示例请求：curl -X POST http://127.0.0.1:5000/collect/steady_state_determination -d "value=输入功率-输出功率>1"
        """
        # 设置当前的稳态判断逻辑
        value = request.get_json().get("value")
        status = auto_collector.set_steady_state_determination(value)
        return jsonify({"status": status}), 200
    else:
        return jsonify({"status": False}), 400


@autocollect.route("/emailset", methods=["GET", "POST"])
def email_set():
    """
    设置邮件发送的相关参数
    示例请求：curl -X POST http://127.0.0.1:5000/collect/emailset -d "sender_mail=12345&sender_passwd=12345"
    """
    if request.method == "GET":
        return (
            jsonify(
                {"sender_mail": emailsender.sender_mail, "receiver_email": emailsender.receiver_email, "receiver_name": emailsender.receiver_name}
            ),
            200,
        )
    else:
        # sender_mail = request.form.get("sender_mail")
        # sender_passwd = request.form.get("sender_passwd")
        receiver_name = request.form.get("receiver_name")
        receiver_email = request.form.get("receiver_email")
        # if sender_mail and sender_passwd:
        #     emailsender.set_sender_mail(sender_mail, sender_passwd)
        status = False
        if receiver_name:
            if receiver_email:
                status = emailsender.set_receiver(receiver_name, receiver_email)
            else:
                status = emailsender.set_receiver(receiver_name, "")
        if status:
            return jsonify({"status": True}), 200
        else:
            return jsonify({"status": False}), 400
