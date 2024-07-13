import mysql.connector
from mysql.connector import Error
import csv
import re
from abc import ABC, abstractmethod


class MySQLBase:
    def __init__(self, host_name, user_name, user_password, db_name, table_name, table_columns):
        self.connection = self.create_connection(host_name, user_name, user_password, db_name)
        self.table_name = table_name
        self.columns = {col_name: dtype for col_name, dtype in table_columns.items() if col_name != "ID"}

    def create_connection(self, host_name, user_name, user_password, db_name):
        try:
            return mysql.connector.connect(host=host_name, user=user_name, passwd=user_password, database=db_name)
        except Error as e:
            print(f"发生错误: {e}")
            return None

    def create_table(self):
        if self.connection and self.connection.is_connected():
            cursor = self.connection.cursor()
            # 动态创建表结构，确保列定义格式正确
            column_definitions = ",\n                ".join([f"{name} {data_type}" for name, data_type in self.table_columns.items()])
            # 确保列定义后没有多余的逗号
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS `{self.table_name}` (
                {column_definitions}
            );
            """
            try:
                cursor.execute(create_table_sql)
                self.connection.commit()
                print(f"表 '{self.table_name}' 创建成功。")
            except mysql.connector.Error as e:  # 确保使用正确的异常类型
                print(f"创建表失败: {e}")
            finally:
                cursor.close()

    @abstractmethod
    def creat_table(self):
        pass

    def select_ids(self, conditions=None):
        """
        根据给定的条件查询数据的ID，并返回一个包含所有ID的列表。
        :param conditions: 附加的查询条件，格式为字符串。
        """
        cursor = self.connection.cursor()
        try:
            # 准备查询语句
            query = f"SELECT ID FROM {self.table_name}"
            # 添加WHERE子句（如果有）
            if conditions:
                query += f" WHERE {conditions}"
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
                # 确保ID列总是被查询，除非用户明确指定不查询ID
                selected_columns = columns if "ID" in columns else columns + ["ID"]
                query += ", ".join(selected_columns)
            else:
                # 查询所有定义的列以及ID列
                all_columns = list(self.columns.keys()) + ["ID"]
                query += ", ".join(all_columns)

            # 添加FROM子句
            query += f" FROM {self.table_name}"

            # 准备WHERE子句
            where_clauses = []
            if ids:
                where_clauses.append(f"ID IN ({','.join(['%s'] * len(ids))})")
            if conditions:
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
        # ids_input的形式为：[4, 5, 6]。若输入为1,2,3或者1-3,5这种可调用self.parse_ids_input(ids_input)
        if ids_input is None:
            self.clear_and_reset_ids()
            query = f"DELETE FROM {self.table_name}"
        else:
            ids = self.parse_ids_input(ids_input)
            placeholders = ", ".join(["%s"] * len(ids))
            query = f"DELETE FROM {self.table_name} WHERE ID IN ({placeholders})"

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, ids if ids_input else ())
            self.connection.commit()
            if ids_input is None:
                print("成功删除所有记录。")
            else:
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
            cursor.execute(f"TRUNCATE TABLE {self.table_name}")
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
        try:
            cursor = self.connection.cursor()
            # 某些情况下，ALTER TABLE 可能不适用于某些存储引擎，例如InnoDB
            cursor.execute(f"ALTER TABLE {self.table_name} AUTO_INCREMENT = 1")
            self.connection.commit()
        except Error as e:
            print(f"发生数据库错误: {e}")
            self.connection.rollback()
        finally:
            if cursor:
                cursor.close()

    def insert_data(self, data_list):
        # data_list的形式为:[{'风机名称': '示例风机3', '风机型号': '型号C', '转速': '1200', '速度环补偿系数': '2', '电流环带宽': '300', '观测器补偿系数': '1.2', '负
        # 载量': '900', '功率': '3'}]
        if not self.connection or not self.connection.is_connected():
            print("数据库连接未建立或已关闭。")
            return

        cursor = self.connection.cursor()
        try:
            # 检查data_list是否为空
            if not data_list:
                print("没有提供要插入的数据。")
                return

            # 确保数据列表中的字典不包含ID列
            for data in data_list:
                if "ID" in data:
                    del data["ID"]  # 移除ID列，假设ID由数据库自动增加

            # 提取列名，排除ID列
            columns = ", ".join([col for col in data_list[0].keys()])

            # 为每个列创建一个对应数量的占位符
            placeholders = ", ".join(["%s"] * len(data_list[0]))

            # 构造插入语句
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"

            # 准备数据元组列表，每个元组对应一个INSERT语句的参数
            data_tuples = [tuple(data.values()) for data in data_list]

            # 执行插入操作
            cursor.executemany(query, data_tuples)
            self.connection.commit()

            print(f"成功插入{len(data_list)}行数据。")

        except mysql.connector.Error as e:
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

        # 构造 SET 子句
        set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])

        # 使用动态表名
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE ID IN ({','.join(['%s'] * len(ids))})"

        # 准备更新值和ID的参数列表
        update_values = list(update_data.values())  # 更新数据的值
        id_params = ids  # ID的参数列表
        values = update_values + list(ids)  # 合并参数列表

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

    def select_data_with_pagination(self, page, per_page):
        with self.connection.cursor() as cursor:
            offset = (page - 1) * per_page
            # 使用动态表名
            cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            total_count = cursor.fetchone()[0]

            # 使用动态表名
            cursor.execute(f"SELECT * FROM {self.table_name} LIMIT %s OFFSET %s", (per_page, offset))
            data = cursor.fetchall()

            return data, total_count

    def get_column_names(self):
        with self.connection.cursor() as cursor:
            # 使用动态表名
            cursor.execute(f"SELECT * FROM {self.table_name} LIMIT 1")
            column_names = [i[0] for i in cursor.description]
        return column_names

    def export_data_with_conditions_to_csv(self, ids_input=None, filename=None, additional_conditions=""):
        if not filename:
            raise ValueError("必须提供CSV文件名")

        with self.connection.cursor() as cursor:
            try:
                ids = None
                if ids_input:
                    ids = [int(id_str.strip()) for id_str in ids_input.split(",") if id_str.strip().isdigit()]

                query = f"SELECT * FROM {self.table_name}"  # 使用动态表名
                where_clauses = []

                if ids:
                    where_clauses.append("ID IN ({})".format(",".join(["%s"] * len(ids))))
                if additional_conditions:
                    where_clauses.append(additional_conditions)

                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)

                cursor.execute(query, ids if ids else ())

                rows = cursor.fetchall()
                columns = [column[0] for column in cursor.description]

                if not rows:
                    print("没有找到符合条件要导出的数据。")
                    return

                dict_rows = [dict(zip(columns, row)) for row in rows]

                if not dict_rows:
                    print("没有找到符合条件要导出的数据。")
                    return

                with open(filename, mode="w", newline="", encoding="utf-8-sig") as file:
                    csv_writer = csv.writer(file)
                    csv_writer.writerow(columns)  # 写入列标题
                    for row_dict in dict_rows:
                        csv_writer.writerow(list(row_dict.values()))  # 写入数据行

                print(f"数据已成功导出到CSV文件：{filename}")

            except Error as e:
                print(f"查询失败：{e}")
                return []

    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
