from .mysql_base import MySQLDatabase
from .table_name_control import TableName

outputdb = MySQLDatabase("localhost", "root", "511427", "world")
table_name = TableName()
