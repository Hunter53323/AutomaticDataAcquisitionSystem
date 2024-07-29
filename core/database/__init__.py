from .mysql_base import MySQLDatabase

TABLE_NAME = "test_table"
TABLE_COLUMNS = {
    "ID": "INT AUTO_INCREMENT PRIMARY KEY",
    # "风机名称": "VARCHAR(255) NOT NULL",  # 风机的名称，不允许为空
    # "风机型号": "VARCHAR(255) NOT NULL",  # 风机的型号，不允许为空
    "设定转速": "INT",  # 风机的转速，以整数形式存储
    "目标转速": "INT",  # 风机的转速，以整数形式存储
    "实际转速": "INT",  # 风机的转速，以整数形式存储
    "速度环补偿系数": "FLOAT",  # 速度环的补偿系数，浮点数类型
    "电流环带宽": "FLOAT",  # 电流环的带宽，浮点数类型
    "观测器补偿系数": "FLOAT",  # 观测器的补偿系数，浮点数类型
    "负载量": "INT",  # 风机的负载量，以整数形式存储
    "输入功率": "FLOAT",  # 风机的功率，浮点数类型
    "输出功率": "FLOAT",  # 风机的功率，浮点数类型
    "效率": "FLOAT",  # 风机的效率，浮点数类型
    "故障": "VARCHAR(255)",  # 风机的故障码，以整数形式存储
    "时间戳": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",  # 记录的时间戳，默认为当前时间
}
TABLE_TRANSLATE = {
    "ID": "ID",
    # "name": "风机名称",
    # "model": "风机型号",
    "speed": "转速",
    "speed_loop_compensates_bandwidth": "速度环补偿系数",
    "current_loop_compensates_bandwidth": "电流环带宽",
    "observer_compensates_bandwidth": "观测器补偿系数",
    "load": "负载量",
    "motor_input_power": "输入功率",
    "motor_output_power": "输出功率",
    "efficiency": "效率",
    "timestamp": "时间戳",
    "target_speed": "目标转速",
    "actual_speed": "实际转速",
    "dc_bus_voltage": "直流母线电压",
    "U_phase_current": "U相电流",
    "power": "功率",
    # "breakdown": "故障",
    "set_speed": "设定转速",
    "torque": "转矩",
}

outputdb = MySQLDatabase("localhost", "liuqi", "liuqi9713", "world", TABLE_NAME, TABLE_COLUMNS)
outputdb.create_table()
