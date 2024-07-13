from flask import Flask, render_template, url_for, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
# from core.communication import communicator
# from core.auto_collection import auto_collector
import threading

############新增数据库模块导入
from flask import Flask, request, jsonify, render_template
from core.database import outputdb
import math
############################3


app = Flask(__name__)
CORS(app, supports_credentials=True)
socketio = SocketIO(app)

# communicator.connect()
# communicator.start_read_all()

thread = None
thread_running = threading.Event()


@app.route("/")
def index():
    return render_template("index.html")

# 路由到第二个index.html
@app.route('/second')
def index_database():
    return render_template('index_database.html')


# 初始化数据库连接

outputdb.create_table()  # 创建表结构


@app.route('/api/data', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_data():
    if request.method == 'POST':
        # 处理数据插入
        data_list = request.get_json().get('data_list', [])
        outputdb.insert_data(data_list)
        return jsonify({'status': 'success', 'message': 'Data inserted successfully'})
    elif request.method == 'GET':
        # 默认为GET请求，返回数据列表
        ids_input = request.args.get('ids_input', None)
        columns = request.args.getlist('columns', None)
        conditions = request.args.get('conditions', None)
        if ids_input:
            # 分割字符串，并转换为整数列表
            ids = [int(id_str) for id_str in ids_input.split(',')]
        else:
            ids = None
        selected_data = outputdb.select_data(ids_input=ids, columns=columns, conditions=conditions)
        return jsonify(selected_data)
    elif request.method == 'PUT':
        # 处理数据更新
        data = request.get_json()
        ids = data.get('ids')
        update_data = data.get('update_data')
        # 将ids字符串转换为整数列表
        ids = [int(id_str) for id_str in ids.split(',') if id_str.isdigit()]
        outputdb.update_data(ids, update_data)
        return jsonify({'status': 'success', 'message': 'Data updated successfully'})
    elif request.method == 'DELETE':
        # 处理数据删除
        ids_input = request.get_json().get('ids_input')
        outputdb.delete_data_by_ids(ids_input)
        return jsonify({'status': 'success', 'message': 'Data deleted successfully'})

@app.route('/api/export', methods=['GET'])
def api_export():
    # filename = 'fans_data1.csv'
    filename = request.args.get('filename')
    ids_input = request.args.get('ids_input', None)
    print(ids_input)
    additional_conditions = request.args.get('additional_conditions', '')
    print(additional_conditions)
    try:
        outputdb.export_data_with_conditions_to_csv(ids_input=ids_input, additional_conditions=additional_conditions, filename=filename)
        return jsonify({'status': 'success', 'message': f'Data exported to {filename}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/api/data/page', methods=['GET'])
def api_showall():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    offset = (page - 1) * per_page
    cursor = outputdb.connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM 风机数据")
        total_count = cursor.fetchone()[0]
        cursor.execute("SELECT * FROM 风机数据 LIMIT %s OFFSET %s", (per_page, offset))
        data = cursor.fetchall()
        total_pages = (total_count + per_page - 1) // per_page  # 计算总页数
        return jsonify({
            'data': data,
            'page': page,
            'per_page': per_page,
            'total_count': total_count,  # 确保返回总记录数
            'total_pages': total_pages  # 返回计算后的总页数
        })
    finally:
        cursor.close()

@app.route('/api/clear_data', methods=['DELETE'])
def api_clear_data():
    # 调用数据库的删除函数，例如删除所有ID的数据
    outputdb.delete_data_by_ids(None)  # None 表示删除所有数据
    return jsonify({'status': 'success', 'message': 'Database cleared successfully'})


if __name__ == "__main__":
    socketio.run(app, debug=True, host="127.0.0.1", port=5000)
