from driver.Driver import DriverBase


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


class TestDriver2(DriverBase):
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
        self.curr_data["data3"] = 3
        self.curr_data["data4"] = 4
        pass


def main():
    data = ["data1", "data2"]
    para = ["para1", "para2"]
    test_driver = TestDriver1("TestDevice", data, para)
    test_driver.connect()
    print(test_driver.conn_state)

    test_driver.start_read_all()
    print(test_driver.read())
    print(test_driver.read("data1"))

    test_driver.write({"para1": 100})

    print(test_driver.get_curr_para())
    print(test_driver.get_curr_para("para1"))

    test_driver.stop_read_all()


if __name__ == "__main__":
    main()
