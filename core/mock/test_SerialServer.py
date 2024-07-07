from SerialServer import handle_command, calculate_checksum

def test_handle_command():
    # 测试控制命令
    data1 = b'\xA5\x01\x01\x03\x00\x00\x01\x00\x01\x00\x01\x00\x01\xAF\x5A'
    # print("Test Control:", handle_command(data1) == b'\x5A\xFF\x01\x01\x01\x5F\xA5')
    assert handle_command(data1) == b'\x5A\xFF\x01\x01\x01\x5F\xA5'
    # 测试查询命令
    data2 = b'\xA5\x01\x02\x00\xA9\x5A'
    # print("Test Search:", handle_command(data2) == b'\x5A\xFF\x02\x0C\x00\xC8\x01\x2C\x00\x32\x00\x64\x00\x1E\x00\x00\x13\xA5')
    assert handle_command(data2) == b'\x5A\xFF\x02\x0C\x00\xC8\x01\x2C\x00\x32\x00\x64\x00\x1E\x00\x00\x13\xA5'

def test_calculate_checksum():
    # 测试校验和
    byte5 = calculate_checksum(b'\x5A', b'\x01', b'\x01', b'\x01', b'\x01', b'\x01')
    # print("Test checksum:", byte5 == b'\x5F')
    assert byte5 == b'\x5F'