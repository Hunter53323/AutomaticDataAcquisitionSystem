from . import db
from core.database import outputdb
from flask import request, jsonify


@db.route("/data", methods=["GET", "POST", "PUT", "DELETE"])
# 数据库的展示操作，数据的获取，增删改查
def sqldb():
    if request.method == "POST":
        # 处理数据插入
        data_list = request.get_json().get("data_list", [])
        outputdb.insert_data(data_list)
        return jsonify({"status": "success", "message": "Data inserted successfully"})
    elif request.method == "GET":
        # 默认为GET请求，返回数据列表
        ids_input = request.args.get("ids_input", None)
        columns = request.args.getlist("columns", None)
        conditions = request.args.get("conditions", None)
        if ids_input:
            # 分割字符串，并转换为整数列表
            ids = [int(id_str) for id_str in ids_input.split(",")]
        else:
            ids = None
        selected_data = outputdb.select_data(ids_input=ids, columns=columns, conditions=conditions)
        return jsonify(selected_data)
    elif request.method == "PUT":
        # 处理数据更新
        data = request.get_json()
        ids = data.get("ids")
        update_data = data.get("update_data")
        # 将ids字符串转换为整数列表
        ids = [int(id_str) for id_str in ids.split(",") if id_str.isdigit()]
        outputdb.update_data(ids, update_data)
        return jsonify({"status": "success", "message": "Data updated successfully"})
    elif request.method == "DELETE":
        # 处理数据删除
        ids_input = request.get_json().get("ids_input")
        outputdb.delete_data_by_ids(ids_input)
        return jsonify({"status": "success", "message": "Data deleted successfully"})


@db.route("/data/page", methods=["GET"])
def api_showall():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    offset = (page - 1) * per_page
    cursor = outputdb.connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM 风机数据")
        total_count = cursor.fetchone()[0]
        cursor.execute("SELECT * FROM 风机数据 LIMIT %s OFFSET %s", (per_page, offset))
        data = cursor.fetchall()
        total_pages = (total_count + per_page - 1) // per_page  # 计算总页数
        return jsonify(
            {
                "data": data,
                "page": page,
                "per_page": per_page,
                "total_count": total_count,  # 确保返回总记录数
                "total_pages": total_pages,  # 返回计算后的总页数
            }
        )
    finally:
        cursor.close()


@db.route("/export", methods=["POST"])
# 数据导出接口，根据发送的测试人员等信息导出数据，返回csv文件，由客户指定导出目录进行保存
def export():
    # filename = 'fans_data1.csv'
    filename = request.args.get("filename")
    ids_input = request.args.get("ids_input", None)
    print(ids_input)
    additional_conditions = request.args.get("additional_conditions", "")
    print(additional_conditions)
    try:
        outputdb.export_data_with_conditions_to_csv(filename=filename, ids_input=ids_input, additional_conditions=additional_conditions)
        return jsonify({"status": "success", "message": f"Data exported to {filename}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@db.route("/clear_data", methods=["DELETE"])
def api_clear_data():
    # 调用数据库的删除函数，例如删除所有ID的数据
    outputdb.delete_data_by_ids()  # None 表示删除所有数据
    return jsonify({"status": "success", "message": "Database cleared successfully"})
