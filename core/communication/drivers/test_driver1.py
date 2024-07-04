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
        pass

