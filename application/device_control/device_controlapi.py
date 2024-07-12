from device_control import control


@control.route("/testdevice", methods=["POST"])
# 测试设备控制
def upload_csv():
    """
    接收文件，返回需要自动采集的数据条数
    """
    pass


@control.route("/fan", methods=["POST"])
# 风机控制
def auto_collect_control():
    """
    接收"signal": "start", "stop", "pause", "continue"
    返回{"status": "start", "stop", "pause", "continue", "complete":True or False}
    """
    pass
