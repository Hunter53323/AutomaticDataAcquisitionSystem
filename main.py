from engineio.async_drivers import gevent
from gevent import monkey

monkey.patch_all(socket=False)
# 以上部分会将thread等模块替换掉，必须放在最前面多线程会出问题，同时由于是阻塞式的逻辑，需要把socket的替换给去掉
from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS
from application.auto_collection import autocollect
from application.database import db
from application.device_control import control
from application.websocket.real_time_dataapi import init_socketio_events
from engineio.async_drivers import gevent


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="gevent")
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
def index_database():
    return render_template("index_database.html")


def get_apis():
    # 获取当前所有api
    print(app.url_map)


if __name__ == "__main__":
    socketio.run(app, debug=True, host="127.0.0.1", port=5000, allow_unsafe_werkzeug=True)
    # httpserver = WSGIServer(("127.0.0.1", 5000), app, log=None)
    # httpserver.serve_forever()


# 考虑浏览器页面意外关闭，也就是disconnect的时候，如何处理，如果有正在进行的自动采集，那么需要暂停自动采集
# TODO：1.数据库导出的时候选择文件目录与文件名
# TODO：2.数据库的ID应该怎么去弄
# TODO：3.数采稳定判别逻辑最好移植到单独的函数里面去，写后清空当前数据后的判断考虑是否有更完善的方案
# TODO：4.可以完成自动采集以及自动存储数据，加上一个从当前数据直接存储的功能
