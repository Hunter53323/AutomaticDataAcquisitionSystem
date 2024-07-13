from .output_database import OutputDatabase

# 定义表名变量
table_name = "风机数据"

# 定义参数名称（表的列）以及相关参数限制
table_columns = {
    "ID": "INT AUTO_INCREMENT PRIMARY KEY",  # 自增主键
    "风机名称": "VARCHAR(255) NOT NULL",  # 风机的名称，不允许为空
    "风机型号": "VARCHAR(255) NOT NULL",  # 风机的型号，不允许为空
    "转速": "INT",  # 风机的转速，以整数形式存储
    "速度环补偿系数": "FLOAT",  # 速度环的补偿系数，浮点数类型
    "电流环带宽": "FLOAT",  # 电流环的带宽，浮点数类型
    "观测器补偿系数": "FLOAT",  # 观测器的补偿系数，浮点数类型
    "负载量": "INT",  # 风机的负载量，以整数形式存储
    "功率": "FLOAT",  # 风机的功率，浮点数类型
    "时间戳": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",  # 记录的时间戳，默认为当前时间
    # 可以根据需要添加更多列
}

outputdb = OutputDatabase("localhost", "liuqi", "liuqi9713", "world", table_name, table_columns)