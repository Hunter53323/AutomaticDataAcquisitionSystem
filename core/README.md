# core 模块管理注意事项

## 文件命名

所有文件以小写字母命名，单词使用下划线 `_` 拼接

## 模块引用

模块内文件使用**相对引用**，子模块需要编写合适的 `__init__.py` 文件，如下 `communication` SubMocule 所示

- `communication`
  - `__init__.py`
  - `communication.py`
  - `drivers`
    - `__init__.py`
    - `driver_base.py`
    - `test_driver1.py`
    - `test_driver2.py`

`communication.py` 中引用 `drivers` SubSubModule 中的驱动程序基类文件 `driver_base.py` 中的 `DriverBase` 类需要使用如下代码

```python
from .drivers.driver_base import DriverBase
```

注意上述代码中 `.drivers.driver_base` 为**相对路径**，可以观看[相关视频](https://www.bilibili.com/video/BV1K24y1k7XA?vd_source=b2425bbb781dff215db471eb24eeaa00)了解相对路径和绝对路径的区别，以及模块管理中使用相对路径的好处

由于本项目只需要一个 `Communication` 对象，且分别只需要一个 `TestDriver1` `TestDriver2` 对象，因此在 `communication/__init__.py` 以及 `communication/drivers/__init__.py` 中直接进行了对象的实例化以及驱动管理工作

```python
# communication/__init__.py

from .communication import communicator
from .drivers import driver1, driver2

communicator = Communication()
communicator.register_device(driver1)
communicator.register_device(driver2)
```

```python
# `communication/drivers/__init__.py`

from .test_driver1 import TestDriver1
from .test_driver2 import TestDriver2
driver1 = TestDriver1("TestDevice1", ["data1", "data2"], ["para1", "para2"])
driver2 = TestDriver2("TestDevice2", ["data3", "data4"], ["para3", "para4"])

```

后期若需考虑拓展性可以将该部分代码移植到软件启动时的 Config 流程中完成

## 调用模块方法及注意事项

由于 `commuication` 模块已经完成了对象的实例化，因此调用此模块时使用如下方法即可直接获取目标对象，而无需在使用前实例化 `Communication` 类并注册 `drivers`

```python
from core.communication import communicator

communicator.connect()
communicator.start_read_all()
communicator.read()
communicator.get_curr_para()
communicator.stop_read_all()
communicator.disconnect()
```

PS 以上内容同样适用于 `auto_collectoion` SubModule