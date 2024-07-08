from .fan_drive_module import FanDriver
import pytest


class TestFanDriver:

    @pytest.fixture(scope="class")
    def init(self):
        fan_driver = FanDriver(
            device_name="Fan",
            data_list=["target_speed", "actual_speed", "dc_bus_voltage", "U_phase_current", "power", "breakdown"],
            para_list=[
                "command",
                "set_speed",
                "speed_loop_compensates_bandwidth",
                "current_loop_compensates_bandwidth",
                "observer_compensates_bandwidth",
            ],
            device_address="01",
            cpu="M4",
        )
        fan_driver.connect()
        return fan_driver

    def test_serwrite(self, init: FanDriver):
        assert init._FanDriver__serwrite(b"\xA5\x02\x5A") == (True, "")

    def read_all_cpu(self, init: FanDriver, cpu: str):
        init.set_device_cpu(cpu)
        assert init.read_all() == True
        target_speed = init.curr_data["target_speed"]
        actual_speed = init.curr_data["actual_speed"]
        dc_bus_voltage = init.curr_data["dc_bus_voltage"]
        U_phase_current = init.curr_data["U_phase_current"]
        power = init.curr_data["power"]
        breakdown = init.curr_data["breakdown"]

        FB, VB, IB, Cofe1, Cofe2, Cofe3, Cofe4, Cofe5 = init._FanDriver__get_cpu_paras()
        assert target_speed == 200 * FB * Cofe1 / Cofe2
        assert actual_speed == 300 * FB * Cofe1 / Cofe2
        assert dc_bus_voltage == 50 * VB / Cofe2
        assert U_phase_current == 100 * IB / Cofe2 / Cofe5
        assert power == 30 * VB * IB * Cofe3 / Cofe4 / Cofe2 / Cofe5
        assert breakdown == []

    def test_read_all_M0(self, init: FanDriver):
        self.read_all_cpu(init, "M0")

    def test_read_all_M4(self, init: FanDriver):
        self.read_all_cpu(init, "M4")

    def test_write(self, init: FanDriver):
        # 初步测试通过，没有测试异常状态
        assert (
            init.write(
                {
                    "command": "start",
                    "set_speed": 100,
                    "speed_loop_compensates_bandwidth": 200,
                    "current_loop_compensates_bandwidth": 300,
                    "observer_compensates_bandwidth": 400,
                }
            )
            == True
        )

    def test_decode_response(self, init: FanDriver):
        # 第一个cpu
        FB, VB, IB, Cofe1, Cofe2, Cofe3, Cofe4, Cofe5 = init._FanDriver__get_cpu_paras()
        assert init._FanDriver__decode_read_response(b"\x5A\xFF\x02\x0C\x00\xC8\x01\x2C\x00\x32\x00\x64\x00\x1E\x00\x00\x10\xA5") == (
            200 * FB * Cofe1 / Cofe2,
            300 * FB * Cofe1 / Cofe2,
            50 * VB / Cofe2,
            100 * IB / Cofe2 / Cofe5,
            30 * IB * VB * Cofe3 / Cofe4 / Cofe2 / Cofe5,
            [],
        )

        init.set_device_cpu("M0")
        FB, VB, IB, Cofe1, Cofe2, Cofe3, Cofe4, Cofe5 = init._FanDriver__get_cpu_paras()
        assert init._FanDriver__decode_read_response(b"\x5A\xFF\x02\x0C\x00\xC8\x01\x2C\x00\x32\x00\x64\x00\x1E\x00\x00\x10\xA5") == (
            200 * FB * Cofe1 / Cofe2,
            300 * FB * Cofe1 / Cofe2,
            50 * VB / Cofe2,
            100 * IB / Cofe2 / Cofe5,
            30 * IB * VB * Cofe3 / Cofe4 / Cofe2 / Cofe5,
            [],
        )


if __name__ == "__main__":
    test = TestFanDriver()
    fan = test.init()
    test.test_read_all_M4(fan)
