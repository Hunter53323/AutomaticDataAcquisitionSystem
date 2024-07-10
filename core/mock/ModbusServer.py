from pymodbus.server import StartSerialServer, StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer


def run_server():
    datablock = ModbusSequentialDataBlock.create()
    context = ModbusSlaveContext(
        di=datablock,
        co=datablock,
        hr=datablock,
        ir=datablock,
    )

    # Build data storage
    context = ModbusServerContext(slaves=context, single=True)

    address = ("0.0.0.0", 503)
    StartTcpServer(
        context=context,  # Data storage
        address=address,  # listen address
    )
    # StartSerialServer(context=context, framer=ModbusRtuFramer, port="COM9", baudrate=9600)


if __name__ == "__main__":
    run_server()
