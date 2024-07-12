from . import autocollect


@autocollect.route("/csvupload", methods=["POST"])
# 上传设备数据采集相关的csv文件
def upload_csv():
    """
    接收文件，返回需要自动采集的数据条数
    """
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
