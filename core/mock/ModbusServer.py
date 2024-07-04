from pymodbus.server import StartSerialServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer


def run_server():
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [17] * 100),
        co=ModbusSequentialDataBlock(0, [17] * 100),
        hr=ModbusSequentialDataBlock(0, [17] * 100),
        ir=ModbusSequentialDataBlock(0, [17] * 100),
    )
    context = ModbusServerContext(slaves=store, single=True)

    # 请确保将以下端口更改为您的USB转串行端口（例如"/dev/ttyUSB0"或"/dev/serial0"）
    StartSerialServer(context=context, framer=ModbusRtuFramer, port="COM9", baudrate=9600)


if __name__ == "__main__":
    run_server()
