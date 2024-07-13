from . import autocollect
from flask import request, jsonify
import csv
from werkzeug.datastructures import FileStorage


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
        csv_data: str = file.read().decode("utf-8")
        line_count = csv_data.count("\n")  # 行数等于换行符数量加1
        # 处理CSV数据，例如解析、保存到数据库等
        # ...
        return jsonify({"line_count": line_count}), 200

    return jsonify({"message": "Unknown error"}), 500
    pass


@autocollect.route("/control", methods=["POST"])
# 自动数采的控制，包括启动、停止、暂停、停止、继续
def auto_collect_control():
    """
    接收"signal": "start", "stop", "pause", "continue"
    返回{"status": "start", "stop", "pause", "continue", "complete":True or False}
    """
    pass


@autocollect.route("/view", methods=["GET"])
# 查看当前的数采进度
def get_current_progress():
    """
    返回{"current_data": current_data, "current_para":{"para1":value},"complete": False}
    """
    pass
