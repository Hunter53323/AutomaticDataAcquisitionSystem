from concurrent_log_handler import ConcurrentRotatingFileHandler
import mysql.connector
from mysql.connector import Error, MySQLConnection
import csv
import re
import os
from datetime import datetime
import logging


class MySQLDatabase:
    def __init__(self, host_name: str, user_name: str, user_password: str, db_name: str):
        self.connection: MySQLConnection
        self.__host_name: str = host_name
        self.__user_name: str = user_name
        self.__user_password: str = user_password
        self.__db_name: str = db_name
        self.table_name: str = None
        self.table_columns: dict[str, str] = {}
        self.columns: dict = {}

        self.table_name_list: list = []
        self.table_columns_list: list = []
        self.columns_list: list[dict] = []
        self.logger = self.set_logger()

        self.create_connection()

    def change_current_table(self, table_name: str, table_columns: dict[str, str] = {}) -> bool:
        """
        切换当前数据库表，如果表不存在则创建。
        :param table_name: 要切换到的表名。
        :param table_columns: 要创建的表的列名和数据类型。
        """
        if not self.check_connection():
            return False
        if table_name not in self.table_name_list:
            if not table_columns:
                self.logger.error(f"表'{table_name}'不存在，且未提供列定义。")
                return False
            self.table_name_list.append(table_name)
            self.table_columns_list.append(table_columns)
            self.columns_list.append({col_name: dtype for col_name, dtype in table_columns.items() if col_name != "ID"})

            self.table_name = table_name
            self.table_columns = table_columns
            self.columns = {col_name: dtype for col_name, dtype in table_columns.items() if col_name != "ID"}
            if not self.check_exists(table_name, table_columns):
                self.logger.error(f"表 '{table_name}' 不存在，创建表。")
                # 如果表不存在，则创建新表
                self.create_table()
            else:
                pass
                # self.logger.info(f"已切换到表 '{table_name}'")
                # self.logger.info(f"表结构：{self.table_columns}")
        else:
            table_name_index = self.table_name_list.index(table_name)
            self.table_name = table_name
            self.table_columns = self.table_columns_list[table_name_index]
            self.columns = self.columns_list[table_name_index]
            # self.logger.info(f"已切换到表 '{table_name}'")
            # self.logger.info(f"表结构：{self.table_columns}")
        return True

    def change_history_table(self, table_name: str) -> bool:
        # 首先检查表是否存在
        if not self.check_connection():
            return False
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            if not cursor.fetchone():
                self.logger.error(f"表 '{table_name}' 不存在，无法切换。")
                return False
            self.table_name = table_name
            self.table_columns = self.get_columns_from_table(table_name)
            self.columns = {col_name: dtype for col_name, dtype in self.table_columns.items() if col_name != "ID"}
            self.logger.info(f"已切换到历史表 '{table_name}'")
            return True
        except Error as e:
            self.logger.error(f"切换历史表时发生错误: {e}")
            return False
        finally:
            cursor.close()

    def get_columns_from_table(self, table_name: str) -> dict:
        """
        获取指定表的列名和数据类型。
        :param table_name: 要查询的表名。
        :return: 包含列名和数据类型的字典。
        """
        if not self.check_connection():
            return {}
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
            columns = cursor.fetchall()
            column_dict = {name: data_type for name, data_type, _, _, _, _ in columns}
            return column_dict
        except Error as e:
            self.logger.error(f"获取表 '{table_name}' 的列时发生错误: {e}")
            return {}
        finally:
            cursor.close()

    def check_exists(self, table_name: str, table_columns: dict[str, str]) -> bool:
        if not self.check_connection():
            return False
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            if not cursor.fetchone():
                self.logger.info(f"表 {table_name}' 不存在，将创建新表。")
                return False
            cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
            columns = cursor.fetchall()
            if len(columns) != len(table_columns):
                self.logger.error(f"表 '{table_name}' 的列数与提供的列定义不匹配。")
                return False
            else:
                for column in columns:
                    name, data_type, is_nullable, extra, _, _ = column
                    if name == "ID" or name == "时间戳":
                        continue
                    if name not in table_columns.keys() or table_columns[name].lower() != data_type:
                        self.logger.error(f"表 '{table_name}' 的列 '{column[0]}' 与提供的列定义不匹配。")
                        return False
            return True
        except Error as e:
            self.logger.error(f"检查表是否存在时发生错误: {e}")
            return False
        finally:
            cursor.close()

    def set_logger(self):
        # 创建一个日志记录器
        logger = logging.getLogger(self.__db_name)
        logger.setLevel(logging.DEBUG)  # 设置日志级别
        formatter = logging.Formatter("%(asctime)s-%(module)s-%(funcName)s-%(lineno)d-%(name)s-%(message)s")
        rHandler = ConcurrentRotatingFileHandler(
            filename="./log/" + self.__db_name + ".log",
            maxBytes=10*1024*1024,  # 设置每个日志文件的最大大小（例如10MB）
            backupCount=1  # 设置保留的日志文件数量
        )
        rHandler.setLevel(logging.DEBUG)
        rHandler.setFormatter(formatter)

        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(formatter)

        logger.addHandler(rHandler)
        logger.addHandler(console)
        return logger

    def create_connection(self) -> bool:
        try:
            self.connection = mysql.connector.connect(
                host=self.__host_name, user=self.__user_name, passwd=self.__user_password, database=self.__db_name
            )
            return True
        except Error as e:
            self.logger.error(f"数据库连接发生错误: {e}")
            return False

    def check_connection(self) -> bool:
        if self.connection.is_connected():
            return True
        else:
            return self.create_connection()

    def create_table(self) -> bool:
        if not self.check_connection():
            return False
        # 动态创建表结构，确保列定义格式正确
        column_definitions = ",\n                ".join([f"`{name}` {data_type}" for name, data_type in self.table_columns.items()])
        # 确保列定义后没有多余的逗号
        create_table_sql = f"""
        CREATE TABLE `{self.table_name}` (
            {column_definitions}
        ) character set = utf8;
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS {self.table_name}")
            cursor.execute(create_table_sql)
            self.connection.commit()
            self.logger.info(f"数据库表 '{self.table_name}' 创建成功。")
            self.logger.info(f"表结构：{self.table_columns}")
            return True
        except mysql.connector.Error as e:  # 确保使用正确的异常类型‘
            self.logger.error(f"创建表失败: {e}")
            self.logger.info(f"表结构：{self.table_columns}")
            return False
        finally:
            cursor.close()

    def select_ids(self, conditions: str = None) -> list:
        """
        根据给定的条件查询数据的ID，并返回一个包含所有ID的列表。
        :param conditions: 附加的查询条件，格式为字符串。
        """
        if not self.check_connection():
            return []
        try:
            cursor = self.connection.cursor()
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
            self.logger.error(f"查询失败：{e}")
            return []
        finally:
            cursor.close()

    def select_data(self, ids_input: list = [], columns: list = [], conditions: str = None) -> list:
        """
        根据指定ID和其他条件查询数据的任意参数。支持混合输入，例如 [1, 2, 3], ["1-2", 3], 或 ["1-3"]。
        :param ids_input: ID输入，可以是具体ID列表、连续ID范围或混合格式。
        :param columns: 要查询的列名列表，如果为None，则查询所有列。
        :param conditions: 附加的查询条件，格式为字符串，例如 "转速 > 1000 AND 风机型号 = '类型A'"。
        """
        if not self.check_connection():
            return []

        try:
            cursor = self.connection.cursor()
            # 解析ID输入
            ids = self.parse_ids_input(ids_input) if ids_input else None

            # 准备基本查询语句
            query = "SELECT "

            # 如果指定了列名，则加入列名列表，否则查询所有列
            if columns:
                # 确保ID列总是被查询，除非用户明确指定不查询ID
                selected_columns = ["ID"] + columns if "ID" in columns else columns
                query += ", ".join(selected_columns)
            else:
                # 查询所有定义的列以及ID列
                all_columns = ["ID"] + list(self.columns.keys())
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
            self.logger.error(f"查询失败：{e}")
            return []
        finally:
            cursor.close()

    def delete_data_by_ids(self, ids_input: list = []) -> bool:
        # ids_input的形式为：[4, 5, 6]。若输入为1,2,3或者1-3,5这种可调用self.parse_ids_input(ids_input)
        if not self.check_connection():
            return False

        if not ids_input:
            self.clear_and_reset_ids()
            return True
        else:
            ids = self.parse_ids_input(ids_input)
            placeholders = ", ".join(["%s"] * len(ids))
            query = f"DELETE FROM {self.table_name} WHERE ID IN ({placeholders})"

        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {self.table_name} WHERE ID IN ({placeholders})", ids)
            count = cursor.fetchone()[0]
            if count == len(ids):
                cursor.execute(query, ids if ids_input else ())
                self.connection.commit()
                if not ids_input:
                    self.logger.info("成功删除所有记录。")
                else:
                    self.logger.info(f"成功删除了ID为{ids}的记录。")
                return True
            else:
                self.logger.error(f"要删除的ID中存在不存在的记录。")
                return False
        except Error as e:
            self.logger.error(f"发生数据库错误: {e}")
            self.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

    def clear_and_reset_ids(self) -> bool:
        """
        删除所有数据并重置ID为0。
        """
        if not self.check_connection():
            return False
        try:
            cursor = self.connection.cursor()
            # 使用 TRUNCATE TABLE 来删除所有数据并重置ID
            cursor.execute(f"TRUNCATE TABLE {self.table_name}")
            self.connection.commit()
            self.logger.info("所有数据已删除，并且ID已经重置。")
            return True
        except Error as e:
            self.logger.error(f"发生数据库错误: {e}")
            self.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

    def rearrange_ids(self):
        """
        删除数据后，对数据的ID重新编排确保其连续性。
        """
        if not self.check_connection():
            return False
        try:
            cursor = self.connection.cursor()
            # 某些情况下，ALTER TABLE 可能不适用于某些存储引擎，例如InnoDB
            cursor.execute(f"ALTER TABLE {self.table_name} AUTO_INCREMENT = 1")
            self.connection.commit()
            return True
        except Error as e:
            self.logger.error(f"发生数据库错误: {e}")
            self.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

    def insert_data(self, data_list: list[dict]) -> bool:
        for data_dict in data_list:
            if not self.insert_one_data([data_dict]):
                return False
        return True

    def insert_one_data(self, data_list: list[dict]) -> bool:
        if len(data_list) != 1:
            return False

        if not self.check_connection():
            return False

        try:
            cursor = self.connection.cursor()
            # 检查data_list是否为空
            if not data_list:
                self.logger.error("没有提供要插入的数据。")
                return True

            # 从data_list中的第一个字典提取列名
            columns = list(data_list[0].keys())
            data_dict = data_list[0]
            data = {}

            for key in data_dict.keys():
                if data_dict[key]:
                    data[key] = data_dict[key]
                else:
                    columns.remove(key)

            # 为每个列创建一个对应数量的占位符
            placeholders = ", ".join(["%s"] * len(columns))

            # 构造插入语句
            query = f"INSERT INTO {self.table_name} (`{'`, `'.join(columns)}`) VALUES ({placeholders})"

            # 准备数据元组列表，每个元组对应一个INSERT语句的参数
            data_tuples = [tuple(data[column] for column in columns)]

            # 执行插入操作
            cursor.executemany(query, data_tuples)

            self.connection.commit()

            self.logger.info(f"成功插入{len(data_list)}行数据。")
            return True

        except mysql.connector.Error as e:
            self.logger.error(f"发生数据库错误: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    def update_data(self, ids: list, update_data: dict) -> bool:
        """
        根据单个或多个指定ID对相应数据的任意参数进行修改。
        :param ids: 要更新的ID列表。
        :param update_data: 要更新的数据，字典格式，键为列名，值为要更新的值。
        """
        if not self.check_connection():
            return False

        if not ids or not update_data:
            self.logger.error("没有提供要更新的ID或数据。")
            return False
        # 构造 SET 子句
        set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])

        # 使用动态表名
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE ID IN ({','.join(['%s'] * len(ids))})"

        # 准备更新值和ID的参数列表
        update_values = list(update_data.values())  # 更新数据的值
        values = update_values + ids  # 合并参数列表
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, values)
            self.connection.commit()
            print(f"成功更新{cursor.rowcount}条记录。")

        except mysql.connector.Error as e:
            print(f"发生数据库错误: {e}")
            self.connection.rollback()
        finally:
            cursor.close()

    def parse_ids_input(self, ids_input: list) -> list:
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
                    self.logger.error(f"不支持的ID格式: {item}")

        return flat_list

    def select_data_with_pagination(self, page: int, per_page: int) -> tuple[list, int]:
        with self.connection.cursor() as cursor:
            offset = (page - 1) * per_page
            # 使用动态表名
            cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            total_count = cursor.fetchone()[0]

            # 使用动态表名
            cursor.execute(f"SELECT * FROM {self.table_name} LIMIT %s OFFSET %s", (per_page, offset))
            data = cursor.fetchall()

            return data, total_count

    def get_column_names(self) -> list:
        with self.connection.cursor() as cursor:
            # 使用动态表名
            cursor.execute(f"SELECT * FROM {self.table_name} LIMIT 1")
            column_names = [i[0] for i in cursor.description]
        return column_names

    def export_data_with_conditions_to_csv(
        self, filename: str, filepath: str = "", ids_input: str = "", additional_conditions: str = ""
    ) -> tuple[bool, str, str]:
        """
        文件目录如果为空则默认导出到程序根目录，否则按照用户输入进行导出
        """
        if not filepath:
            # 创建一个名为 export 的文件夹
            export_folder = os.path.join(os.getcwd(), "export")
            if not os.path.exists(export_folder):
                os.makedirs(export_folder)
        else:
            export_folder = filepath

        # # 获取当前时间戳
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # # 构建新的文件名，包括时间戳
        # new_filename = f"{filename}_{timestamp}.csv"

        # 构建完整的文件路径
        full_path = os.path.join(export_folder, filename)

        with self.connection.cursor() as cursor:
            try:
                ids = []
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
                    return False, "没有找到符合条件要导出的数据", ""

                dict_rows = [dict(zip(columns, row)) for row in rows]

                if not dict_rows:
                    return False, "没有找到符合条件要导出的数据", ""

                with open(full_path, mode="w", newline="", encoding="utf-8-sig") as file:
                    csv_writer = csv.writer(file)
                    csv_writer.writerow(columns)  # 写入列标题
                    for row_dict in dict_rows:
                        csv_writer.writerow(list(row_dict.values()))  # 写入数据行

                return True, f"数据已成功导出到CSV文件:{full_path}", full_path

            except Error as e:
                return False, "未知异常", ""

    def close_connection(self):
        if self.connection.is_connected():
            self.connection.close()
