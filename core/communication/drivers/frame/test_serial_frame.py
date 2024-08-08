from serial_frame import Framer

class TestFramer():
    ff=Framer()

    def test_setheader(self):
        assert self.ff.set_header(b"\x5A")[0] is True
        assert self.ff.set_header(b"UY")[0] is False
        assert self.ff.set_header(b"\x55a")[0] is False
        assert self.ff.set_header(b"\x55\x5a")[0] is False
        assert self.ff.set_header(b"xnihao")[0] is False
        assert self.ff.set_header("?")[0] is False

    # def test_setField(self):
    #     n = Field(index=1, name="speed", type="int", size=2, formula="real_data=(raw_data+2)/3")
    #     n.raw_data = 12
    #     print(n.formula)
    #     print(n.inv_formula)
    #     n.evaluate_formula()
    #     print(n.real_data)
    #     n.evaluate_formula(to_real=False)
    #     print(n.raw_data)
    def test_setdata(self):
        ff = Framer()
        assert ff.set_data(index=1, name="speed", type="double", size=2, formula="real_data=(raw_data+2)/3")[0] is False
        assert ff.set_data(index=1, name="speed", type="int16", size=2, formula="real_data=(raw_data+2)/3")[0] is True
        assert ff.set_data(index=1, name="power", type="int16", size=2, formula="real_data=(raw_data+2)/3")[0] is False
        assert ff.set_data(index=2, name="power", type="int16", size=2, formula="real_data=(data+2)/3")[0] is False
        # assert ff.set_data(index=2, name="power", type="int16", size=2, formula="data=(raw_data+2)/3")[0] is False
        assert ff.set_data(index=2, name="power", type="int16", size=2, formula="real_data=(raw_data+2)/3")[0] is True
        assert ff.set_data(index=4, name="breakdown", type="bit16", size=2, formula="")[0] is True
        ff.cofirm_framer(b'\xA5\xFF\x00\x03\x00\x01\x00\x02\x03\x03\x01\x02\xb4\x5A')
        data = ff.get_data()
        print(data)