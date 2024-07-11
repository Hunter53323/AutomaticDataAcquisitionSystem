from . import fandriver
import pytest


class TestFanDriver:

    # @pytest.fixture(scope="class")
    # def init(self):
    #     return fan_driver

    # def test_serwrite(self):
    #     assert fandriver._FanDriver__serwrite(b"\xA5\x02\00\x5A") == (True, "")

    def read_all_cpu(self, cpu: str):
        fandriver.set_device_cpu(cpu)
        assert fandriver.read_all() == True
        target_speed = fandriver.curr_data["target_speed"]
        actual_speed = fandriver.curr_data["actual_speed"]
        dc_bus_voltage = fandriver.curr_data["dc_bus_voltage"]
        U_phase_current = fandriver.curr_data["U_phase_current"]
        power = fandriver.curr_data["power"]
        breakdown = fandriver.curr_data["breakdown"]

        FB, VB, IB, Cofe1, Cofe2, Cofe3, Cofe4, Cofe5 = fandriver._FanDriver__get_cpu_paras()
        # assert target_speed == 200 * FB * Cofe1 / Cofe2
        # assert actual_speed == 300 * FB * Cofe1 / Cofe2
        # assert dc_bus_voltage == 50 * VB / Cofe2
        # assert U_phase_current == 100 * IB / Cofe2 / Cofe5
        # assert power == 30 * VB * IB * Cofe3 / Cofe4 / Cofe2 / Cofe5
        # assert breakdown == []

    def test_read_all_M0(self):
        self.read_all_cpu("M0")

    def test_read_all_M4(self):
        self.read_all_cpu("M4")

    def test_write(self):
        # 初步测试通过，没有测试异常状态
        assert (
            fandriver.write(
                {
                    "fan_command": "start",
                    "set_speed": 100,
                    "speed_loop_compensates_bandwidth": 2323,
                    "current_loop_compensates_bandwidth": 300,
                    "observer_compensates_bandwidth": 400,
                }
            )
            == True
        )

    # def test_breakdown(self):#测试成功，再次测试需要将SerialServer的response = handle_command(data, fan,True)
    #     fandriver.set_device_cpu("M0")
    #     for i in range(65536):
    #         assert fandriver.read_all() == True
    #         breakdown = fandriver.curr_data["breakdown"]


    # def test_wALL(self):#测试完成没有问题，时间约3h过长后面不再测试了
    #     for speed in range(65536):
    #         print(speed)
    #         assert (
    #                 fandriver.write(
    #                     {
    #                         "fan_command": "start",
    #                         "set_speed": speed,
    #                         "speed_loop_compensates_bandwidth": 10,
    #                         "current_loop_compensates_bandwidth": 300,
    #                         "observer_compensates_bandwidth": 400,
    #                     }
    #                 )
    #                 == True
    #         )
    #     for speed_loop_compensates_bandwidth in range(15, 3100):
    #         print(speed_loop_compensates_bandwidth)
    #         assert (
    #                 fandriver.write(
    #                     {
    #                         "fan_command": "start",
    #                         "set_speed": 10,
    #                         "speed_loop_compensates_bandwidth": speed_loop_compensates_bandwidth,
    #                         "current_loop_compensates_bandwidth": 300,
    #                         "observer_compensates_bandwidth": 400,
    #                     }
    #                 )
    #                 == True
    #         )

    def test_decode_response(self):
        # 第一个cpu
        FB, VB, IB, Cofe1, Cofe2, Cofe3, Cofe4, Cofe5 = fandriver._FanDriver__get_cpu_paras()
        assert fandriver._FanDriver__decode_read_response(b"\x5A\xFF\x02\x0C\x00\xC8\x01\x2C\x00\x32\x00\x64\x00\x1E\x00\x00\x10\xA5") == (
            200 * FB * Cofe1 / Cofe2,
            300 * FB * Cofe1 / Cofe2,
            50 * VB / Cofe2,
            100 * IB / Cofe2 / Cofe5,
            30 * IB * VB * Cofe3 / Cofe4 / Cofe2 / Cofe5,
            [],
        )

        fandriver.set_device_cpu("M0")
        FB, VB, IB, Cofe1, Cofe2, Cofe3, Cofe4, Cofe5 = fandriver._FanDriver__get_cpu_paras()
        assert fandriver._FanDriver__decode_read_response(b"\x5A\xFF\x02\x0C\x00\xC8\x01\x2C\x00\x32\x00\x64\x00\x1E\x00\x00\x10\xA5") == (
            200 * FB * Cofe1 / Cofe2,
            300 * FB * Cofe1 / Cofe2,
            50 * VB / Cofe2,
            100 * IB / Cofe2 / Cofe5,
            30 * IB * VB * Cofe3 / Cofe4 / Cofe2 / Cofe5,
            [],
        )

    def test_update_parameter(self):
        assert fandriver.update_hardware_parameter({"device_address": b"\x01", "cpu": "M0"}) == True
        assert fandriver.update_hardware_parameter({"cpu": "M0"}) == True
        assert fandriver.update_hardware_parameter({"device_address": b"\x01"}) == True
        assert fandriver.update_hardware_parameter({"device_address": b"\x01", "cpu": "M3"}) == False
        assert fandriver.update_hardware_parameter({"device_address": b"\x01", "k1": "M0"}) == False

    def test_close(self):
        assert fandriver.disconnect() == True


if __name__ == "__main__":
    test = TestFanDriver()
    fan = test.fandriver()
    test.test_read_all_M4(fan)
