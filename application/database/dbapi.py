from . import db
from core.database import outputdb
from flask import request, jsonify
from core.statement.statement import generate_pdf
from core.database import table_name
from flask import send_file


@db.route("/data", methods=["GET", "POST", "PUT", "DELETE"])
# 数据库的展示操作，数据的获取，增删改查
def sqldb():
    if not outputdb.change_current_table(table_name.get_table_name()):
        if not outputdb.change_history_table(table_name.get_table_name()):
            return jsonify({"status": "error", "message": "表不存在"}), 404
    if request.method == "POST":
        # 处理数据插入
        data_list = request.get_json().get("data_list", [])
        if outputdb.insert_data([data_list]):
            return jsonify({"status": "success", "message": "Data inserted successfully"})
        else:  # 数据插入失败
            return jsonify({"status": "error", "message": "Data insert failed"})
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
        outputdb.update_data(ids, update_data)
        return jsonify({"status": "success", "message": "Data updated successfully"})
    elif request.method == "DELETE":
        # 处理数据删除
        ids_input = request.get_json().get("ids_input")
        outputdb.delete_data_by_ids(ids_input)
        return jsonify({"status": "success", "message": "Data deleted successfully"})


@db.route("/data/page", methods=["GET"])
def api_showall():
    if not outputdb.change_current_table(table_name.get_table_name()):
        if not outputdb.change_history_table(table_name.get_table_name()):
            return jsonify({"status": "error", "message": "表不存在"}), 404
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    offset = (page - 1) * per_page
    cursor = outputdb.connection.cursor()
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {outputdb.table_name}")
        total_count = cursor.fetchone()[0]
        cursor.execute(
            f"SELECT * FROM {outputdb.table_name} LIMIT %s OFFSET %s",
            (per_page, offset),
        )
        data = cursor.fetchall()
        total_pages = (total_count + per_page - 1) // per_page  # 计算总页数

        column_names = [desc[0] for desc in cursor.description]
        data_with_column_names = [dict(zip(column_names, row)) for row in data]
        # print(data_with_column_names)

        return jsonify(
            {
                "data": data,
                "page": page,
                "per_page": per_page,
                "total_count": total_count,  # 确保返回总记录数
                "total_pages": total_pages,  # 返回计算后的总页数
            }
        )
    except Exception as e:
        return jsonify({"message": "读取数据失败，" + str(e)}), 500
    finally:
        cursor.close()


@db.route("/data/meta", methods=["GET"])
def api_show_meta():
    if not outputdb.change_current_table(table_name.get_table_name()):
        if not outputdb.change_history_table(table_name.get_table_name()):
            return jsonify({"status": "error", "message": "表不存在"}), 404
    cursor = outputdb.connection.cursor()
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {outputdb.table_name}")
        total_count = cursor.fetchone()[0]
        cursor.execute(f"SELECT * FROM {outputdb.table_name} LIMIT %s OFFSET %s", (1, 0))
        data = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        column_names_to_fill = column_names.copy()
        column_names_to_fill.remove("ID")
        column_names_to_fill.remove("时间戳")
        # print(column_names)
        # print(column_names_to_fill)
        return jsonify({"columns": column_names, "columns_to_fill": column_names_to_fill, "total_count": total_count})
    except Exception as e:
        return jsonify({"message": "读取数据列名失败，" + str(e)}), 500
    finally:
        cursor.close()


@db.route("/data/pagev2", methods=["GET"])
def api_showall_v2():
    if not outputdb.change_current_table(table_name.get_table_name()):
        if not outputdb.change_history_table(table_name.get_table_name()):
            return jsonify({"status": "error", "message": "表不存在"}), 404
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    offset = (page - 1) * per_page
    cursor = outputdb.connection.cursor()
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {outputdb.table_name}")
        total_count = cursor.fetchone()[0]
        cursor.execute(
            f"SELECT * FROM {outputdb.table_name} LIMIT %s OFFSET %s",
            (per_page, offset),
        )
        data = cursor.fetchall()

        column_names = [desc[0] for desc in cursor.description]
        data_with_column_names = [dict(zip(column_names, row)) for row in data]
        # print(data_with_column_names)

        total_pages = (total_count + per_page - 1) // per_page  # 计算总页数
        return jsonify(
            {
                "data": data_with_column_names,
                "page": page,
                "per_page": per_page,
                "total_count": total_count,  # 确保返回总记录数
                "total_pages": total_pages,  # 返回计算后的总页数
            }
        )
    except Exception as e:
        return jsonify({"message": "读取数据失败，" + str(e)}), 500
    finally:
        cursor.close()


@db.route("/export", methods=["GET"])
# 数据导出接口，根据发送的测试人员等信息导出数据，返回csv文件，由客户指定导出目录进行保存
def export():
    # filename = 'fans_data1.csv'
    filename = request.args.get("filename")
    ids_input = request.args.get("ids_input", "")
    additional_conditions = request.args.get("additional_conditions", "")
    try:
        if not outputdb.change_current_table(table_name.get_table_name()):
            if not outputdb.change_history_table(table_name.get_table_name()):
                return jsonify({"status": "error", "message": "表不存在"}), 404
        status, err, export_filepath = outputdb.export_data_with_conditions_to_csv(
            filename=filename,
            ids_input=ids_input,
            additional_conditions=additional_conditions,
        )
        if status:
            return send_file(export_filepath, as_attachment=True)
        else:
            return jsonify({"status": "error", "message": "Data export failed"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@db.route("/statement", methods=["POST"])
# 报表生成接口，根据发送的测试人员等信息生成报表，返回excel文件，由客户指定导出目录进行保存
def statement():
    """
    示例:
    curl -X POST http://127.0.0.1:5000/db/statement \
        -H "Content-Type: application/json" \
        -d '{"ids_input": [1,2,3,4,"5-10"], "draw_parameters": ["负载量", "设定转速"], "data_column": ["负载量", "设定转速", "速度环补偿系数", "电流环带宽", "观测器补偿系数", "目标转速", "实际转速"], "input_form": {"实验员姓名": "张三", "公司名称": "XX公司"} }'
    """
    # filename = request.args.get("filename")
    input_form = request.get_json().get("input_form")
    ids_input: list[int | str] = request.get_json().get("ids_input", "")
    draw_parameters: list[str] = request.get_json().get("draw_parameters", "")
    data_column: list[str] = request.get_json().get("data_column", "")
    try:
        if not outputdb.change_current_table(table_name.get_table_name()):
            if not outputdb.change_history_table(table_name.get_table_name()):
                return jsonify({"status": "error", "message": "表不存在"}), 404
        data = outputdb.select_data(ids_input=ids_input, columns=data_column)
        if "ID" not in data_column:
            data_column.insert(0, "ID")
        data_dict_list = [dict(zip(data_column, row)) for row in data]
        export_path = generate_pdf(draw_parameters, input_form, data_dict_list)
        return send_file(export_path, as_attachment=True)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
