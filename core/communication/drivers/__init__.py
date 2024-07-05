from .test_driver1 import TestDriver1
from .test_driver2 import TestDriver2

driver1 = TestDriver1(
    "TestDevice1",
    [
        "data1",
        "data2",
        "moredata1",
        "moredata2",
        "moredata3",
        "moredata4",
        "moredata5",
        "moredata6",
        "moredata7",
    ],
    ["para1", "para2"],
)
driver2 = TestDriver2("TestDevice2", ["data3", "data4"], ["para3", "para4"])
