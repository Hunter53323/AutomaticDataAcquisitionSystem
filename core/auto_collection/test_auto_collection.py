from ..auto_collection import auto_collector
from ..communication import communicator


def test_auto_collector():
    # communicator.connect()
    # communicator.start_read_all()
    auto_collector.init_para_pool(
        {
            "set_speed": [1, 2],
            "speed_loop_compensates_bandwidth": [1, 2],
            "current_loop_compensates_bandwidth": [1, 2],
            "observer_compensates_bandwidth": [1, 2],
            "load": [1, 2],
        }
    )
    auto_collector.auto_collect()
