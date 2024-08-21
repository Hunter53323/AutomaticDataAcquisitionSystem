from pymodbus.server import (
    StartTcpServer,
)
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)

datablock = ModbusSequentialDataBlock.create()
context = ModbusSlaveContext(
    di=datablock,
    co=datablock,
    hr=datablock,
    ir=datablock,
)
single = True

# Build data storage
store = ModbusServerContext(slaves=context, single=single)


if __name__ == "__main__":

    address = ("0.0.0.0", 5020)
    StartTcpServer(
        context=store,  # Data storage
        address=address,  # listen address
    )
