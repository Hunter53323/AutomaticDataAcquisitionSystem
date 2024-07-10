from core.communication import communicator
from core.auto_collection import auto_collector


def test_communicator():
    print("连接设备，并启动读取功能")
    communicator.connect()
    communicator.start_read_all()
    print()

    print("读取全部 Data 测试")
    print(communicator.read())
    print()
    print("读取单个 Data 测试")
    print(communicator.read(["data1"]))
    print()

    print("读取 Para 测试")
    print(communicator.get_curr_para())
    print()

    print("设置 Para 测试")
    communicator.write({"para1": 100, "para3": 999, "para2": 12312})
    print()

    print("读取修改后全部 Para 测试")
    print(communicator.get_curr_para())
    print()
    print("读取修改后多个 Para 测试")
    print(communicator.get_curr_para(["para1", "para3"]))

    communicator.stop_read_all()


def test_auto_collector():
    communicator.connect()
    communicator.start_read_all()
    auto_collector.init_para_pool(
        {
            "para1": [1, 2, 3, 4],
            "para2": [100, 200, 300, 400],
            "para3": [5, 15, 25],
            "para4": [7, 8, 9],
        }
    )
    auto_collector.auto_collect()


if __name__ == "__main__":
    test_communicator()
    # test_auto_collector()
