from .auto_collection import AutoCollection
from core.communication import communicator
from core.database import outputdb

auto_collector = AutoCollection(communicator, outputdb)
