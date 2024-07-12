from .auto_collection import AutoCollection
from ..communication import communicator
from ..database import outputdb

auto_collector = AutoCollection(communicator, outputdb)
