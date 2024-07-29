from io import StringIO
from . import autocollect
from flask import request, jsonify
import csv
from werkzeug.datastructures import FileStorage
from core.auto_collection import auto_collector
from core.database import TABLE_TRANSLATE

column_mapping = {
    "转速": "set_speed",
    "速度环补偿系数": "speed_loop_compensates_bandwidth",
    "电流环带宽": "current_loop_compensates_bandwidth",
    "观测器补偿系数": "observer_compensates_bandwidth",
    "负载量": "load",
}


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
        # 将 csv_context 转换为所需的格式
        CH2EN = {}
        translated_csv_context = []

        for row in csv_context:
            if "ID" in row:
                del row["ID"]
            elif "\ufeffID" in row:
                del row["\ufeffID"]
            else:
                return jsonify({"message": "文件编码错误,请使用utf-8格式的csv文件"}), 400
            translated_row = {}
            for CHkey, value in row.items():
                if CHkey not in CH2EN:
                    for en, ch in TABLE_TRANSLATE.items():
                        if ch == CHkey:
                            CH2EN[ch] = en
                            break
                    else:
                        auto_collector.logger.error(f"没有对应的控制参数：{CHkey}")
                        # TODO value目前只能是整数
                translated_row[CH2EN[CHkey]] = int(value)
            translated_csv_context.append(translated_row)
        auto_collector.init_para_pool_from_csv(translated_csv_context)
        return jsonify({"message": "文件上传成功", "line_count": line_count}), 200

    return jsonify({"message": "Unknown error"}), 500
    pass


@autocollect.route("/control", methods=["POST"])
# 自动数采的控制，包括启动、停止、暂停、停止、继续
def auto_collect_control():
    """
    处理采集数据的开始、停止等请求
    接收"command": "start", "stop", "pause", "continue"
    返回{"status": "start", "stop", "pause", "continue", "complete":True or False}
    """
    command = request.form.get("command")
    if command == "start":
        # 启动数据采集，（所有前期基本参数已经设置好）
        auto_collector.start_auto_collect()
        return jsonify({"status": "start"}), 200
    elif command == "pause":
        # 暂停数采
        auto_collector.pause_auto_collect()
        return jsonify({"status": "pause"}), 200
    elif command == "continue":
        # 恢复数采
        auto_collector.continue_auto_collect()
        return jsonify({"status": "continue"}), 200
    elif command == "stop":
        # 停止数采，是终止，无法再次启动
        auto_collector.stop_auto_collect()
        return jsonify({"status": "stop"}), 200
    elif command == "clear":
        # 清空当前的采集进度
        if auto_collector.clear_para():
            return jsonify({"status": "clear"}), 200
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
