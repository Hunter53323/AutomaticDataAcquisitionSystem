from . import control


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


@control.route("/setdevice", methods=["GET", "POST"])
# 对设备参数进行设置，修改设备名称，D轴电感、Q轴电感等参数
def set_device():
    """
    POST接收到的数据格式为：{"device_name": "fan1", "para_name": "D_coil", "value": 0.1}
    返回的是{"status": True or False}
    GET接收返回的是当前的设备参数，数据格式同上，为全部参数
    """
    pass
