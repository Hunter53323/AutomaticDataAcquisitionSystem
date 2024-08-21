import json
import os

CONFIG_NAME = "base.config"


def save_json(data: dict[str, any]) -> bool:
    check_config()
    try:
        with open(CONFIG_NAME, "r") as f:
            config = json.load(f)
            config.update(data)

        with open(CONFIG_NAME, "w") as f:
            json.dump(config, f)
        return True
    except Exception as e:
        print("save_json", e)
        return False


def read_json(key: str) -> any:
    check_config()
    try:
        with open(CONFIG_NAME, "r") as f:
            config = json.load(f)
            return config.get(key)
    except Exception as e:
        print("read_json", e)
        return None


def delete_json(key: str) -> bool:
    try:
        with open(CONFIG_NAME, "r") as f:
            config = json.load(f)
            config.pop(key)

        with open(CONFIG_NAME, "w") as f:
            json.dump(config, f)
        return True
    except Exception as e:
        print("delete_json", e)
        return False


def check_config():
    # 检查文件是否存在
    if not os.path.exists(CONFIG_NAME):
        # 创建文件
        with open(CONFIG_NAME, "w") as file:
            # 写入空字典
            file.write("{}")
        print(f"文件 {CONFIG_NAME} 已创建并写入空字典。")
