from core.communication.drivers.fan_drive_module import FanDriver
import pytest


class TestFanDriver:

    def test_delete(self):
        fan1 = FanDriver("Fan", device_address="01", cpu="M0", port="COM9")
        len1 = len(fan1.curr_para)
        assert fan1.delete_F_data(f_name="control_f", index=1)[0] == True
        assert fan1.delete_F_data(f_name="control_f", index=10)[0] == False
        assert fan1.delete_F_data(f_name="sdfsdfsd", index=10)[0] == False
        assert len(fan1.curr_para) == len1 - 1
        assert fan1.control_f.encode_framer() == b'\xa5\x01\x01\x08\x00\x00\x00\x00\x00\x00\x00\x00\xaf\x5a'

    def test_update(self):
        fan1 = FanDriver("Fan", device_address="01", cpu="M0", port="COM9")
        assert fan1.updata_F_data(f_name="control_f", index=2, name="修改1", type="bit16", size=2,
                                  formula="")[
                   0] == True
        assert fan1.updata_F_data(f_name="control_f", index=2, name="修改2", type="float", size=2,
                                  formula="real_data=raw_data")[
                   0] == False
        assert fan1.updata_F_data(f_name="control_f", index=2, name="修改3", type="int16", size=2, formula="")[
                   0] == False
        assert fan1.updata_F_data(f_name="control_f", index=2, name="修改4", type="int16", size=2,
                                  formula="real_data=raw_data*2")[
                   0] == True

    def test_export_load(self):
        fan1 = FanDriver("Fan", device_address="01", cpu="M0", port="COM9")
        assert fan1.updata_F_data(f_name="control_f", index=2, name="修改1", type="bit16", size=2,
                                  formula="")[
                   0] == True
        config1 = fan1.export_config()
        curr_para = fan1.curr_para
        fan2 = FanDriver("Fan", device_address="01", cpu="M0", port="COM9")
        assert fan2.updata_F_data(f_name="control_f", index=2, name="修改4", type="int16", size=2,
                                  formula="real_data=raw_data*2")[
                   0] == True
        print(curr_para)
        print(fan2.curr_para)
        # assert curr_para != fan2.curr_para
        assert fan2.load_config(config1)[0] == True
        print(fan2.curr_para)
        # assert curr_para == fan2.curr_para


    # def test_read_all_M0(self):
    #     self.read_all_cpu("M0")
    #
    # def test_read_all_M4(self):
    #     self.read_all_cpu("M4")


if __name__ == "__main__":
    test = TestFanDriver()
