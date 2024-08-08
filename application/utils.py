from core.database import TABLE_TRANSLATE


def cn_translate(en: str):
    """
    将英文参数名翻译为中文
    """
    return TABLE_TRANSLATE.get(en, en)
