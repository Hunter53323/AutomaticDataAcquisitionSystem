from database import db


@db.route("/show", methods=["GET", "POST", "PUT", "DELETE"])
# 数据库的展示操作，数据的获取，增删改查
def sqldb():
    pass


@db.route("/export", methods=["POST"])
# 数据导出接口，根据发送的测试人员等信息导出数据，返回csv文件，由客户指定导出目录进行保存
def export():
    pass
