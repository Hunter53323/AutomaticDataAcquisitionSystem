import pytest
from .mysql_base import MySQLDatabase
from mysql.connector import Error
import os


# 测试前请确保环境变量中有正确的数据库连接信息
HOST = os.getenv('DB_HOST', 'localhost')
USER = os.getenv('DB_USER', 'liuqi')
PASSWORD = os.getenv('DB_PASSWORD', 'liuqi9713')
DB_NAME = os.getenv('DB_NAME', 'world')
TABLE_NAME = "test_table"
TABLE_COLUMNS = {
    "ID": "INT AUTO_INCREMENT PRIMARY KEY",
    "风机名称": "VARCHAR(255) NOT NULL",     # 风机的名称，不允许为空
    "风机型号": "VARCHAR(255) NOT NULL",     # 风机的型号，不允许为空
    "转速": "INT",                            # 风机的转速，以整数形式存储
    "速度环补偿系数": "FLOAT",               # 速度环的补偿系数，浮点数类型
    "电流环带宽": "FLOAT",                  # 电流环的带宽，浮点数类型
    "观测器补偿系数": "FLOAT",              # 观测器的补偿系数，浮点数类型
    "负载量": "INT",                          # 风机的负载量，以整数形式存储
    "功率": "FLOAT",                          # 风机的功率，浮点数类型
    "时间戳": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"  # 记录的时间戳，默认为当前时间
}

@pytest.fixture(scope="module")
def db():
    # 创建数据库实例
    db_instance = MySQLDatabase(HOST, USER, PASSWORD, DB_NAME, TABLE_NAME, TABLE_COLUMNS)
    try:
        # 尝试连接数据库
        connection = db_instance.create_connection(HOST, USER, PASSWORD, DB_NAME)
        yield db_instance
    finally:
        if connection and connection.is_connected():
          # 测试结束后删除测试表并关闭连接
          db_instance.clear_and_reset_ids()
          # 关闭数据库连接
          db_instance.connection.close()           

def test_create_connection(db):
    assert db.connection.is_connected()

# 测试表格构建
def test_create_table(db):
    db.create_table()
    # 使用 select_ids 来确认表不为空
    ids = db.select_ids()
    assert len(ids) == 0  # 确认表是空的，因为没有插入数据

#测试插入功能
def test_insert_data_with_missing_values(db):
    db.clear_and_reset_ids()
    # 准备测试数据
    test_data = [
       {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500, '速度环补偿系数': 0.5, '电流环带宽': 100, '观测器补偿系数': 0.9, '负载量': 500, '功率': 1.5}
       ,{'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500}
       ,{'风机名称': '示例风机1', '风机型号': '型号A'}
    ]
    
    # 插入数据
    db.insert_data(test_data)
    
    # 查询所有数据
    selected_data = db.select_data()
    
    # 验证查询结果数量是否与插入数据匹配
    assert len(selected_data) == len(test_data), "查询到的数据数量与插入的数据不符"
    
    # 确定selected_data中的列数，假设最后两列是ID和时间戳
    num_columns_in_selected_data = len(selected_data[0])
    num_extra_columns = 2  # 假设ID和时间戳是额外的两列

    # 准备用于比较的数据格式，忽略ID和时间戳
    test_data_for_comparison = []
    for data in test_data:
        # 将字典转换为元组，只包含除了ID和时间戳之外的列
        test_data_tuple = tuple(data[key] for key in db.columns.keys() if key in data)
        test_data_for_comparison.append(test_data_tuple)

    # 比较数据，忽略ID和时间戳列
    for test_tuple, selected_tuple in zip(test_data_for_comparison, selected_data):
        # 截取selected_tuple中除了ID和时间戳之外的部分
        selected_tuple_excluding_extra = selected_tuple[:num_columns_in_selected_data - num_extra_columns]
        assert test_tuple == selected_tuple_excluding_extra, "原始数据与查询结果不匹配"


# 测试查询功能，查询所有列且不带条件的情况
def test_select_data_all_columns(db):
    db.clear_and_reset_ids()
    test_data = [
        {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500, '速度环补偿系数': 0.5, '电流环带宽': 100, '观测器补偿系数': 0.9, '负载量': 500, '功率': 1.5},
        {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500},
        {'风机名称': '示例风机1', '风机型号': '型号A'}
    ]
    
    # 插入数据
    db.insert_data(test_data)
    
    # 查询所有数据
    result = db.select_data()
    
    # 假设查询结果中最后两列是ID和时间戳，我们需要去掉这两列
    result_data_without_timestamp_and_id = [row[:-2] for row in result]
    
    # 准备用于比较的数据格式，将字典转换为元组，按照列顺序
    correct_order = ['风机名称', '风机型号', '转速', '速度环补偿系数', '电流环带宽', '观测器补偿系数', '负载量', '功率']
    test_data_tuples = [tuple(data.get(key, None) for key in correct_order) for data in test_data]

    # 验证查询结果数量是否与插入数据匹配
    assert len(result_data_without_timestamp_and_id) == len(test_data_tuples), "查询到的数据数量与插入的数据不符"
    
    # 验证每行数据是否正确
    for result_row in result_data_without_timestamp_and_id:
        assert result_row in test_data_tuples, "原始数据与查询结果不匹配"




# 测试查询功能，通过指定ID查询        
def test_select_data_by_specific_ids(db):
    db.clear_and_reset_ids()
    # 插入多条测试数据
    test_data = [
        {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500, '速度环补偿系数': 0.5, '电流环带宽': 100, '观测器补偿系数': 0.9, '负载量': 500, '功率': 1.5},
        {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500},
        {'风机名称': '示例风机1', '风机型号': '型号A'}
    ]
    db.insert_data(test_data)
    
    # 定义要查询的ID列表
    ids = [1, 3]  # 假设这些ID是数据库中的ID
    
    # 执行查询
    result = db.select_data(ids_input=ids)
    
    
    # 验证查询结果数量，应为 2（ID为1和3的数据）
    assert len(result) == 2, "查询结果的数量不正确"
    
    # 确定正确的列顺序
    correct_order = ['风机名称', '风机型号', '转速', '速度环补偿系数', '电流环带宽', '观测器补偿系数', '负载量', '功率']
    
    # 假设查询结果中包含datetime和ID列，我们需要去掉这两列
    # 并且将结果从元组转换为列表，以便于排序
    result_data_without_timestamp_and_id = [list(row[:-2]) for row in result]
    
    # 将结果数据按照正确的列顺序排列
    result_data_sorted = [dict(zip(correct_order, row)) for row in result_data_without_timestamp_and_id]
    
    # 准备用于比较的数据格式，将字典转换为元组
    test_data_tuples = [tuple(data.get(key, None) for key in correct_order) for data in test_data if data]
    
    # 验证查询结果中的每个参数是否符合预期
    for result_dict in result_data_sorted:
        result_tuple = tuple(result_dict[key] for key in correct_order)
        assert result_tuple in test_data_tuples, "原始数据与查询结果不匹配"


#测试查询功能，仅条件查询
def test_select_data_with_conditions(db):
    db.clear_and_reset_ids()
    test_data = [
        {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500, '速度环补偿系数': 0.5, '电流环带宽': 100, '观测器补偿系数': 0.9, '负载量': 500, '功率': 1.5},
        {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500},
        {'风机名称': '示例风机1', '风机型号': '型号A'}
    ]
    db.insert_data(test_data)
    conditions = "转速 = 1500 AND 速度环补偿系数 = 0.5"
    result = db.select_data(conditions=conditions)
    assert len(result) == 1  # 验证只有一条数据满足条件

    # 准备一个列表，包含原始数据的所有键
    original_keys = list(test_data[0].keys()) if test_data else []
    
    # 将查询结果的元组转换为字典
    result_dicts = [{key: value for key, value in zip(original_keys, row)} for row in result]
    
    # 验证查询结果中的每个参数是否符合预期
    for result_dict in result_dicts:
        # 找到匹配的原始数据项
        for expected_item in test_data:
            if all(result_dict.get(key) == expected_item.get(key, None) for key in original_keys):
                # 如果查询结果中的字典与原始数据项匹配，则认为验证成功
                break
        else:  # 如果没有找到匹配的原始数据项，则断言失败
            assert False, "查询结果中没有找到匹配的原始数据项"    


#测试查询功能，同时使用 ID 和条件查询数据
def test_select_data_with_ids_and_conditions(db):
    db.clear_and_reset_ids()
    # 插入多条测试数据
    test_data = [
        {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500, '速度环补偿系数': 0.5, '电流环带宽': 100, '观测器补偿系数': 0.9, '负载量': 500, '功率': 1.5},
        {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500},
        {'风机名称': '示例风机1', '风机型号': '型号A'}
    ]
    db.insert_data(test_data)
    
    # 定义查询的 ID 列表和查询条件
    ids = [1, 3]  # 查询 ID 为 1 或 3 的数据
    conditions = "转速 = 1500 AND 速度环补偿系数 = 0.5"  
    
    # 执行查询
    result = db.select_data(ids_input=ids, conditions=conditions)
    
    # 验证查询结果数量，应为 1（ID 为 1 的数据满足条件）
    assert len(result) == 1, "查询结果的数量不正确"
    
    # 准备一个列表，包含原始数据的所有键
    original_keys = list(test_data[0].keys()) if test_data else []
    
    # 将查询结果的元组转换为字典
    result_dicts = [{key: value for key, value in zip(original_keys, row)} for row in result]
    
    # 验证查询结果中的每个参数是否符合预期
    for result_dict in result_dicts:
        # 找到匹配的原始数据项
        for expected_item in test_data:
            if all(result_dict.get(key) == expected_item.get(key, None) for key in original_keys):
                # 如果查询结果中的字典与原始数据项匹配，则认为验证成功
                break
        else:  # 如果没有找到匹配的原始数据项，则断言失败
            assert False, "查询结果中没有找到匹配的原始数据项"

#测试更新功能，单个ID的单个指定参数更新
def test_update_single_id_single_column(db):
    db.clear_and_reset_ids()
    # 插入测试数据
    test_data = [
        {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500},
        {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500},
        {'风机名称': '示例风机1', '风机型号': '型号A'}
    ]
    db.insert_data(test_data)
    
    # 假设插入操作后ID被自动分配，并且我们知道第一个数据的ID是1
    ids = [1]
    update_data = {'转速': 2000}
    db.update_data(ids, update_data)
    
    # 查询更新后的数据
    selected_data = db.select_data(ids_input=ids)
    assert len(selected_data) == 1  # 确保只选到了一条数据
    
    # 将查询结果的元组转换为字典
    updated_data = {key: value for key, value in zip(db.columns.keys() if db.columns else [], selected_data[0])}
    
    # 检查 '转速' 字段是否更新
    assert updated_data['转速'] == update_data['转速'], "更新的 '转速' 字段不正确"

#测试更新功能，多个ID的单个指定参数更新
def test_update_multiple_ids_single_column(db):
    db.clear_and_reset_ids()
    # 插入测试数据
    test_data = [
        {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500},
        {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500},
        {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500}  # 确保所有数据都有 '风机型号'
    ]
    db.insert_data(test_data)
    ids = [1, 2]
    update_data = {'转速': 2000}
    db.update_data(ids, update_data)
    
    # 查询更新后的数据
    selected_data = db.select_data(ids_input=ids)
    # 确保查询结果不为空
    assert len(selected_data) == len(ids), "未选到所有更新的数据"
    
    # 获取列名列表，这里假设 db.columns 已经正确地包含了所有列名
    column_names = list(db.columns.keys())  # 确保列名不为空
    
    # 检查 '转速' 字段是否更新
    for row in selected_data:
        # 将查询结果的每个元组转换为字典
        updated_data_dict = dict(zip(column_names, row))
        # 检查 '转速' 字段是否更新为 2000
        assert updated_data_dict['转速'] == update_data['转速'], "更新的 '转速' 字段不正确"

    print("所有更新的数据检查完成，更新正确。")

#测试删除功能，测试删除单个ID数据
def test_delete_single_id(db):
    db.clear_and_reset_ids()    
    # 插入测试数据，必须有转速和名称
    test_data = [
        {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500},
        {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500},
        {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500}  # 确保所有数据都有 '风机型号'
    ]
    db.insert_data(test_data)
    
    # 删除单个ID的数据
    ids = [1]
    db.delete_data_by_ids(ids)
    
    # 查询尝试获取已删除的数据
    selected_data = db.select_data(ids_input=ids)
    assert len(selected_data) == 0  # 检查数据是否已被删除

#测试删除功能，同时删除多个ID数据
def test_delete_multiple_ids(db):
    db.clear_and_reset_ids()    
    # 插入测试数据，必须有名称和转速
    test_data = [
        {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500},
        {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500},
        {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500}  # 确保所有数据都有 '风机型号'
    ]
    db.insert_data(test_data)
    
    # 删除多个ID的数据
    ids = [1, 2]
    db.delete_data_by_ids(ids)
    
    # 查询尝试获取已删除的数据
    selected_data = db.select_data(ids_input=ids)
    assert len(selected_data) == 0  # 检查数据是否已被删除

 # 测试清空数据库
def test_clear_and_reset_ids(db):
    db.clear_and_reset_ids()    
    # 首先插入一些数据
    test_data = [
        {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500},
        {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500},
        {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500}  # 确保所有数据都有 '风机型号'
    ]
    db.insert_data(test_data)
    # 清空数据并重置ID
    db.clear_and_reset_ids()
    # 检查ID是否重置
    selected_data = db.select_data()
    assert len(selected_data) == 0  # 检查表是否为空

#测试ID计数器重置重排连续ID功能，包含删除数据重排和增加数据重排
def test_rearrange_ids_and_insert(db):
    db.clear_and_reset_ids()    
    # 准备初始测试数据，包含必须的风机名称和风机型号
    initial_data = [
        {"风机名称": "示例风机1", "风机型号": "型号A", "转速": 1500},
        {"风机名称": "示例风机2", "风机型号": "型号B"},
        {"风机名称": "示例风机3", "风机型号": "型号C", "转速": 1700},
    ]

    # 插入初始数据
    db.insert_data(initial_data)

    # 验证初始数据的ID是否连续
    ids_before_deletion = db.select_ids()
    assert ids_before_deletion == [1, 2, 3], "初始ID不连续"

    # 删除ID为2的数据
    db.delete_data_by_ids([2])

    # 验证删除数据后剩余数据的ID是否保持不变
    remaining_ids_after_deletion = db.select_ids()
    assert remaining_ids_after_deletion == [1, 3], "删除数据后ID不连续"

    # 准备新数据，确保包含风机名称和风机型号，ID留空让数据库自动分配
    new_fan_data = [
        {"风机名称": "新示例风机1", "风机型号": "新型号A", "转速": 2000},
        {"风机名称": "新示例风机2", "风机型号": "新型号B", "转速": 2100},
    ]

    # 插入新数据
    db.insert_data(new_fan_data)

    # 查询当前所有ID
    all_ids_after_insert = db.select_ids()

    # 验证新插入的数据的ID是否为连续的下一个ID
    expected_ids_after_insert = [1, 3, 4, 5]  # 假设新插入的数据ID为4和5
    assert all_ids_after_insert == expected_ids_after_insert, "新插入的数据ID不连续"