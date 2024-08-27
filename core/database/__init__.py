from .mysql_base import MySQLDatabase
from .table_name_control import TableName

outputdb = MySQLDatabase("localhost", "haier", "haier357", "adas")
table_name = TableName()
