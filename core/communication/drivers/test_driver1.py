from .driver_base import DriverBase


class TestDriver1(DriverBase):
    def write(self, para_dict: dict[str, any]) -> bool:
        for key, val in para_dict.items():
            self.curr_para[key] = val
        return True

    def connect(self) -> bool:
        self.conn_state = True
        return True

    def disconnect(self) -> bool:
        self.stop_read_all()
        self.conn_state = False
        return True

    def read_all(self) -> bool:
        self.curr_data["data1"] = 1
        self.curr_data["data2"] = 2
        self.curr_data["moredata1"] = 123.123
        self.curr_data["今天是星期天"] = 123123123
        self.curr_data["moredata3"] = 1978
        self.curr_data["moredata4"] = 0002310.3123
        self.curr_data["moredata5"] = 14551
        self.curr_data["moredata6"] = 145
        self.curr_data["moredata7"] = 134511614
        pass

