class TableName:
    def __init__(self):
        self.__table_name = "风机数据"

    def set_table_name(self, table_name: str):
        self.__table_name = table_name

    def get_table_name(self):
        return self.__table_name
