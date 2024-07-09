from .communication import Communication

# from .drivers import driver1, driver2
from .drivers import testdevice, fandriver

communicator = Communication()
# communicator.register_device(driver1)
# communicator.register_device(driver2)
communicator.register_device(testdevice)
communicator.register_device(fandriver)
