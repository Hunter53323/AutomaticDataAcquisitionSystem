import mysql.connector
from mysql.connector import Error
from .mysql_base import MySQLBase
import csv
import re


class OutputDatabase(MySQLBase):
    def __init__(self, host_name, user_name, user_password, db_name, table_name, table_columns):
        # 确保传递所有需要的参数给 MySQLDatabase 的构造函数
        super().__init__(host_name, user_name, user_password, db_name, table_name, table_columns)
        self.table_name = table_name
        self.table_columns = table_columns

    def create_table(self):
        # 调用父类的 create_table 方法
        super().create_table()

    # def create_table(self):
    #     if self.connection and self.connection.is_connected():
    #         cursor = self.connection.cursor()
    #         # 动态创建表结构
    #         column_definitions = ',\n                '.join([
    #             f"{name} {data_type}" for name, data_type in self.table_columns.items()
    #         ])
    #         create_table_sql = f"""
    #         CREATE TABLE IF NOT EXISTS {self.table_name} (
    #             {column_definitions}
    #         )
    #         """
    #         try:
    #             cursor.execute(create_table_sql)
    #             self.connection.commit()
    #             print(f"表 '{self.table_name}' 创建成功。")
    #         except Error as e:
    #             print(f"创建表失败: {e}")
    #         finally:
    #             cursor.close()

    # def create_table(self):
    #     if self.connection and self.connection.is_connected():
    #         cursor = self.connection.cursor()
    #         create_table_sql = """
    #         CREATE TABLE IF NOT EXISTS 风机数据 (
    #             ID INT AUTO_INCREMENT PRIMARY KEY,
    #             风机名称 VARCHAR(255) NOT NULL,
    #             风机型号 VARCHAR(255) NOT NULL,
    #             转速 INT,
    #             速度环补偿系数 FLOAT,
    #             电流环带宽 FLOAT,
    #             观测器补偿系数 FLOAT,
    #             负载量 INT,
    #             功率 FLOAT,
    #             时间戳 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    #         )
    #         """
    #         cursor.execute(create_table_sql)
    #         self.connection.commit()

    #     return super().create_table()
