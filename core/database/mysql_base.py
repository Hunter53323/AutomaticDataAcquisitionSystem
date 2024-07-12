import mysql.connector
from mysql.connector import Error
import csv
import re

class MySQLDatabase:
    def __init__(self, host_name, user_name, user_password, db_name):
        self.connection = self.create_connection(host_name, user_name, user_password, db_name)

    def create_connection(self, host_name, user_name, user_password, db_name):
        try:
            return mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=user_password,
                database=db_name
            )
        except Error as e:
            print(f"发生错误: {e}")
            return None

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

    def create_table(self):
        if self.connection and self.connection.is_connected():
            cursor = self.connection.cursor()
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS 风机数据 (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                风机名称 VARCHAR(255) NOT NULL,
                风机型号 VARCHAR(255) NOT NULL,
                转速 INT,
                速度环补偿系数 FLOAT,
                电流环带宽 FLOAT,
                观测器补偿系数 FLOAT,
                负载量 INT,
                功率 FLOAT,
                时间戳 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_sql)
            self.connection.commit()            


    def select_ids(self, conditions=None):
        """
        根据给定的条件查询数据的ID，并返回一个包含所有ID的列表。
        :param conditions: 附加的查询条件，格式为字符串。
        """
        cursor = self.connection.cursor()
        try:
            # 准备查询语句
            query = "SELECT ID FROM 风机数据"

            # 添加WHERE子句（如果有）
            if conditions:
                query += " WHERE " + conditions

            # 执行查询
            cursor.execute(query)

            # 获取所有ID
            ids = [row[0] for row in cursor.fetchall()]  # 假设ID是每个元组的第一个元素

            return ids

        except Error as e:
            print(f"查询失败：{e}")
            return []
        finally:
            cursor.close()

    def select_data(self, ids_input=None, columns=None, conditions=None):
        """
        根据指定ID和其他条件查询数据的任意参数。支持混合输入，例如 [1, 2, 3], ["1-2", 3], 或 ["1-3"]。
        :param ids_input: ID输入，可以是具体ID列表、连续ID范围或混合格式。
        :param columns: 要查询的列名列表，如果为None，则查询所有列。
        :param conditions: 附加的查询条件，格式为字符串，例如 "转速 > 1000 AND 风机型号 = '类型A'"。
        """
        if not self.connection or not self.connection.is_connected():
            print("数据库连接未建立或已关闭。")
            return []

        cursor = self.connection.cursor()
        try:
            # 解析ID输入
            ids = self.parse_ids_input(ids_input) if ids_input else None

            # 准备基本查询语句
            query = "SELECT "

            # 如果指定了列名，则加入列名列表，否则查询所有列
            if columns:
                query += ", ".join(columns)
            else:
                query += "*"

            # 添加FROM子句
            query += " FROM 风机数据"

            # 准备WHERE子句
            where_clauses = []
            if ids:
                where_clauses.append(f"ID IN ({','.join(['%s'] * len(ids))})")
            if conditions:
                # 假设conditions是一个格式良好的SQL条件字符串
                where_clauses.append(conditions)

            # 如果存在WHERE子句，添加到查询语句
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            # 执行查询
            cursor.execute(query, ids if ids else ())
            return cursor.fetchall()

        except Error as e:
            print(f"查询失败：{e}")
            return []
        finally:
            cursor.close()   



    def delete_data_by_ids(self, ids_input):
        if ids_input is None:
            self.clear_and_reset_ids()
            # 如果 ids_input 是 None，表示需要删除所有数据
            query = "DELETE FROM 风机数据"
            try:
                cursor = self.connection.cursor()
                cursor.execute(query)
                self.connection.commit()
                print("成功删除所有记录。")
            except Error as e:
                print(f"发生数据库错误: {e}")
                self.connection.rollback()
            finally:
                if cursor:
                    cursor.close()
        else:
            # 如果 ids_input 不是 None，按原来的方法解析并删除指定的 ID
            try:
                ids = self.parse_ids_input(ids_input)
                placeholders = ', '.join(['%s'] * len(ids))
                query = f"DELETE FROM 风机数据 WHERE ID IN ({placeholders})"
                cursor = self.connection.cursor()
                cursor.execute(query, ids)
                self.connection.commit()
                print(f"成功删除了ID为{ids}的记录。")
            except Error as e:
                print(f"发生数据库错误: {e}")
                self.connection.rollback()
            finally:
                if cursor:
                    cursor.close()

    def clear_and_reset_ids(self):
        """
        删除所有数据并重置ID为0。
        """
        try:
            cursor = self.connection.cursor()
            # 使用 TRUNCATE TABLE 来删除所有数据并重置ID
            cursor.execute("TRUNCATE TABLE 风机数据")
            self.connection.commit()
            print("所有数据已删除，并且ID已经重置。")
        except Error as e:
            print(f"发生数据库错误: {e}")
            self.connection.rollback()
        finally:
            if cursor:
                cursor.close()            

    def rearrange_ids(self):
        """
        删除数据后，对数据的ID重新编排确保其连续性。
        """
        cursor = self.connection.cursor()
        cursor.execute("ALTER TABLE 风机数据 AUTO_INCREMENT = 1")
        self.connection.commit()

    def insert_data(self, data_list):
        """
        插入任意行数的数据，并在插入后重新编排ID以确保连续性。
        :param data_list: 要插入的数据列表，格式为[{列名1: 值1, 列名2: 值2}, ...]。
        """
        if not self.connection or not self.connection.is_connected():
            print("数据库连接未建立或已关闭。")
            return

        cursor = self.connection.cursor()
        try:
            # 检查data_list是否为空
            if not data_list:
                print("没有提供要插入的数据。")
                return

            # 提取列名
            columns = ', '.join(data_list[0].keys())
            # 为每个列创建一个对应数量的占位符
            placeholders = ', '.join(['%s'] * len(data_list[0]))

            # 构造插入语句
            query = f"INSERT INTO 风机数据 ({columns}) VALUES ({placeholders})"
            
            # 准备数据元组列表，每个元组对应一个INSERT语句的参数
            data_tuples = [tuple(data.values()) for data in data_list]

            # 执行插入操作
            cursor.executemany(query, data_tuples)
            self.connection.commit()

            print(f"成功插入{len(data_list)}行数据。")

            # 插入数据后，重新编排ID以确保连续性
            self.rearrange_ids()

        except Error as e:
            print(f"发生数据库错误: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def update_data(self, ids, update_data):
        """
        根据单个或多个指定ID对相应数据的任意参数进行修改。
        :param ids: 要更新的ID列表。
        :param update_data: 要更新的数据，字典格式，键为列名，值为要更新的值。
        """
        if not self.connection or not self.connection.is_connected():
            print("数据库连接未建立或已关闭。")
            return

        cursor = self.connection.cursor()
        if not ids or not update_data:
            print("没有提供要更新的ID或数据。")
            return

        set_clause = ', '.join([f"{key} = %s" for key in update_data.keys()])
        query = f"UPDATE 风机数据 SET {set_clause} WHERE ID IN ({','.join(['%s'] * len(ids))})"

        # 准备更新值和ID的参数列表
        # 更新数据的值只需要提供一次
        update_values = list(update_data.values())
        # ID的参数列表
        id_params = ids
        # 将更新数据的值和ID的参数合并
        values = update_values + id_params

        try:
            cursor.execute(query, values)
            self.connection.commit()
            print(f"成功更新{cursor.rowcount}条记录。")
        except mysql.connector.Error as e:
            print(f"发生数据库错误: {e}")
            self.connection.rollback()
        finally:
            cursor.close()



    def parse_ids_input(self, ids_input):
        """
        解析ID输入，支持单个ID列表、连续ID范围或混合格式。
        :param ids_input: ID输入，可以是具体ID列表、连续ID范围或混合格式。
        :return: 解析后的ID列表。
        """
        range_regex = re.compile(r'(\d+)-(\d+)')
        flat_list = []

        # 拆分输入以处理单个ID或ID范围
        for item in ids_input:
            if isinstance(item, int):  # 单个ID
                flat_list.append(item)
            else:
                match = range_regex.fullmatch(item)
                if match:  # ID范围
                    start_id, end_id = map(int, match.groups())
                    flat_list.extend(range(start_id, end_id + 1))
                else:
                    raise ValueError(f"不支持的ID格式: {item}")

        return flat_list

    def select_data_with_pagination(self, page, per_page):
        with self.connection.cursor() as cursor:  # 使用 with 语句自动管理游标
            offset = (page - 1) * per_page
            cursor.execute("SELECT COUNT(*) FROM 风机数据")
            total_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT * FROM 风机数据 LIMIT %s OFFSET %s", (per_page, offset))
            data = cursor.fetchall()
            
            return data, total_count
        # 不需要调用 cursor.close()，with 语句会自动处理

    def get_column_names(self):
        with self.connection.cursor() as cursor:  # 使用 with 语句自动管理游标
            cursor.execute("SELECT * FROM 风机数据 LIMIT 1")  # 仅查询一行以获取列名
            column_names = [i[0] for i in cursor.description]  # 获取列名
            # 读取结果集，即使我们不需要这些数据
            _ = cursor.fetchall()
        return column_names
    

    def export_data_with_conditions_to_csv(self, ids_input=None, filename=None, additional_conditions=''):
        if not filename:
            raise ValueError("必须提供CSV文件名")
            
        cursor = self.connection.cursor()
        try:
            # 解析ID输入，如果ids_input为空或None，则返回None
            ids = None
            if ids_input:
                # 移除空格并分割输入
                ids = [int(id_str.strip()) for id_str in ids_input.split(',') if id_str.strip().isdigit()]
            
            # 准备基本查询语句
            query = "SELECT * FROM 风机数据"
            where_clauses = []

            # 准备WHERE子句
            if ids:
                where_clauses.append("ID IN ({})".format(','.join(['%s'] * len(ids))))
            if additional_conditions:
                where_clauses.append(additional_conditions)

            # 如果存在WHERE子句，添加到查询语句
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            # 执行查询
            cursor.execute(query, ids if ids else ())
            # print("执行的SQL查询:", cursor.statement)  # 打印执行的SQL查询

            # 获取查询结果和列标题
            rows = cursor.fetchall()
            # print(rows)
            columns = [column[0] for column in cursor.description]
            # print(columns)

            # 如果查询结果为空，提示用户
            if not rows:
                print("没有找到符合条件要导出的数据。")
                return

            dict_rows = [dict(zip(columns, row)) for row in rows]

            # 如果查询结果为空，提示用户
            if not dict_rows:
                print("没有找到符合条件要导出的数据。")
                return

            # 写入CSV文件
            with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
                csv_writer = csv.writer(file)
                csv_writer.writerow(columns)  # 写入列标题
                for row_dict in dict_rows:
                    csv_writer.writerow(list(row_dict.values()))  # 写入数据行

            print(f"数据已成功导出到CSV文件：{filename}")

        except Error as e:
            print(f"查询失败：{e}")
            return []
        finally:
            cursor.close()   
            
                                    
                
    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()