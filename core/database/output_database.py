import mysql.connector
from mysql.connector import Error
from .mysql_base import MySQLBase
import csv
import re


class OutputDatabase(MySQLBase):
    def __init__(self, host_name, user_name, user_password, db_name):
        super().__init__(host_name, user_name, user_password, db_name)
        self.table_name = "output_data"

    def create_table(self):
        return super().create_table()
