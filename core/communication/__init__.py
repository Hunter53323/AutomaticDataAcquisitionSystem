from .communication import Communication
from .drivers import driver1, driver2

communicator = Communication()
communicator.register_device(driver1)
communicator.register_device(driver2)