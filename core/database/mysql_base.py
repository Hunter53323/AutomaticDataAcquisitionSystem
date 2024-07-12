import mysql.connector
from mysql.connector import Error
import csv
import re


class MySQLBase:
    def __init__(self, host_name, user_name, user_password, db_name):
        self.connection = self.create_connection(host_name, user_name, user_password, db_name)

    def create_connection(self, host_name, user_name, user_password, db_name):
        try:
            return mysql.connector.connect(host=host_name, user=user_name, passwd=user_password, database=db_name)
        except Error as e:
            print(f"发生错误: {e}")
            return None

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
        """
        根据指定ID删除数据，之后对数据的ID重新编排确保其连续性。
        :param ids_input: 要删除的ID的混合输入，可以是具体ID列表、连续ID范围或混合格式。
        """
        if not self.connection or not self.connection.is_connected():
            print("数据库连接未建立或已关闭。")
            return

        cursor = self.connection.cursor()
        try:
            # 解析ID输入
            ids = self.parse_ids_input(ids_input)

            # 准备SQL语句的占位符
            placeholders = ", ".join(["%s"] * len(ids))
            query = f"DELETE FROM 风机数据 WHERE ID IN ({placeholders})"

            # 执行删除操作
            cursor.execute(query, ids)
            self.connection.commit()
            print(f"成功删除了ID为{ids}的记录。")

            # 删除数据后，重新编排ID以确保连续性
            self.rearrange_ids()
        except mysql.connector.Error as e:
            print(f"发生数据库错误: {e}")
            self.connection.rollback()
        finally:
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
            columns = ", ".join(data_list[0].keys())
            # 为每个列创建一个对应数量的占位符
            placeholders = ", ".join(["%s"] * len(data_list[0]))

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

        set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
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
        range_regex = re.compile(r"(\d+)-(\d+)")
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

    def export_data_with_conditions_to_csv(self, ids_input=None, filename=None, additional_conditions=""):
        """
        根据指定的条件导出数据到CSV文件。如果没有指定ID，则导出所有数据。
        :param ids_input: ID输入，可以是具体ID列表、连续ID范围或混合格式。
        :param filename: CSV文件的名称。
        :param additional_conditions: 附加的SQL查询条件语句，可以为空。
        """

        if not filename:
            raise ValueError("必须提供CSV文件名")

        cursor = self.connection.cursor()

        # 解析ID输入，如果ids_input为None或空列表，则ids将为None
        ids = self.parse_ids_input(ids_input) if ids_input else None

        # 准备SQL查询
        if ids:
            ids_placeholder = ", ".join(["%s"] * len(ids))
            conditions = f"ID IN ({ids_placeholder})"
        else:
            conditions = "1=1"  # 无ID条件，始终为真

        # 添加附加条件
        if additional_conditions:
            conditions += f" AND {additional_conditions}"

        query = f"SELECT * FROM 风机数据 WHERE {conditions}"
        cursor.execute(query, ids)
        print("执行的SQL查询:", cursor.statement)  # 打印执行的SQL查询

        # 获取查询结果和列标题
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]

        # 如果查询结果为空，提示用户
        if not rows:
            print("没有找到符合条件要导出的数据。")
            return

        # 写入CSV文件
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(columns)  # 写入列标题
            csv_writer.writerows(rows)  # 写入数据行

        print(f"数据已成功导出到CSV文件：{filename}")

    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()


# 使用示例
if __name__ == "__main__":
    db_config = {"host_name": "localhost", "user_name": "liuqi", "user_password": "liuqi9713", "db_name": "world"}

    db = OutputDatabase(**db_config)
    db.create_table()

    ###########################插入功能#################################################################
    # # 插入数据示例
    # data_list = [
    #     {'风机名称': '示例风机1', '风机型号': '型号A', '转速': 1500, '速度环补偿系数': 0.5, '电流环带宽': 100, '观测器补偿系数': 0.9, '负载量': 500, '功率': 1.5},
    #     # 可以添加更多数据
    # ]
    # db.insert_data(data_list)

    ###########################查询功能#################################################################
    # # 按照给定的ID和特定的列查询，支持混合ID查询
    # ids = [3]  # 假设我们要查询ID为3的风机数据
    # # ids = [3,4]  # 假设我们要查询ID为3和4的风机数据
    # # ids = ['3-5']  # 假设我们要查询ID为3-5的风机数据
    ids = ["1-2", 4]  # 假设我们要查询ID为3-5的风机数据
    if ids == "":
        mixed_ids = None
    else:
        mixed_ids = db.parse_ids_input(ids)
    # mixed_ids = None # 假设我们要查询所有ID的风机数据

    # #假设我们对以下几列感兴趣
    # columns_of_interest = ''    #默认所有列
    # #columns_of_interest = ['风机名称', '转速', '功率']
    # selected_data = db.select_data(ids_input=mixed_ids, columns=columns_of_interest)
    # print(f"查询到的数据: {selected_data}")

    # # 按照给定的参数条件，查询符合要求的数据的ID
    additional_conditions = "转速 > 1000 AND 风机型号 = '型号A'"
    selected_data = db.select_data(conditions=additional_conditions)
    print(f"查询到的数据: {selected_data}")
    # 输出符合条件数据的ID
    ids = db.select_ids(conditions=additional_conditions)
    print("符合条件的ID列表:", ids)  # 直接输出ID列表

    ###########################修改功能#################################################################
    # 修改指定ID的数据
    # ids = ['1-3',4]
    # mixed_ids = db.parse_ids_input(ids)
    # update_data = {'观测器补偿系数': 0.9}
    # db.update_data(mixed_ids, update_data)

    ###########################删除功能#################################################################
    # # 删除指定ID的数据，与查询类似，支持混合ID删除
    ids = ["6-7", 8]
    # ids = ['9-13']
    # # # ids = [3,4]
    # # # ids = [5]
    # mixed_ids = db.parse_ids_input(ids)
    db.delete_data_by_ids(ids)

    ###########################导出功能#################################################################
    # # #导出指定ID的数据，并自行命名csv文件名称，支持混合ID删除
    # csv_filename = 'fans_data.csv'
    # # # 导出所有数据
    # # db.export_data_with_conditions_to_csv(filename=csv_filename)

    # # #导出数据ID设置：导出特定ID的数据，例如ID为1, 2, 3, 4
    # # mixed_ids = [1, 2, 3, 4]
    # # db.export_data_with_conditions_to_csv(ids_input=mixed_ids, filename=csv_filename)

    # # # 导出连续ID范围的数据，例如ID从1到4
    # # mixed_ids = ['1-4']
    # # db.export_data_with_conditions_to_csv(ids_input=mixed_ids, filename=csv_filename)

    # # 导出混合格式的数据，例如ID从1到2，然后是3和4
    # # mixed_ids = ['1-2', 3, 4]
    # # db.export_data_with_conditions_to_csv(ids_input=mixed_ids, filename=csv_filename)

    # #附加条件设置：导出转速大于1000且型号为“类型A”的所有数据
    # mixed_ids = ['1-2', 3, 4]
    # additional_conditions = "转速 > 1000 AND 风机型号 = '型号A'"
    # db.export_data_with_conditions_to_csv(ids_input=mixed_ids, additional_conditions=additional_conditions, filename=csv_filename)

    db.close_connection()


# 以下是功能块的作用说明：
# 1. `select_data`: 允许根据单个或多个指定ID查询数据的任意参数，或者查询指定参数在单个或多个ID下的数值。
# 2. `delete_data_by_ids`: 允许根据指定ID列表删除数据，并调用`rearrange_ids`方法对剩余数据的ID重新编排以确保连续性。
# 3. `insert_data`: 允许插入任意行数的数据，之后调用`rearrange_ids`方法对数据ID重新编排以确保连续性。
# 4. `update_data`: 允许根据单个或多个指定ID对相应数据的任意参数进行修改，或者对指定参数在单个或多个ID下的数值进行修改。
