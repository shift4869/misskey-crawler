from datetime import datetime, timedelta
from typing import Any


def find_values(obj: Any,
                key: str,
                is_predict_one: bool = False,
                key_whitelist: list[str] = [],
                key_blacklist: list[str] = []) -> Any | list[Any]:
    def _inner_helper(inner_obj: Any, inner_key: str, inner_result: list) -> list:
        if inner_key in key_blacklist:
            return inner_result
        if isinstance(inner_obj, dict) and (inner_dict := inner_obj):
            for k, v in inner_dict.items():
                if k == inner_key:
                    inner_result.append(v)
                if key_whitelist and (k not in key_whitelist):
                    continue
                inner_result.extend(_inner_helper(v, inner_key, []))
        if isinstance(inner_obj, list) and (inner_list := inner_obj):
            for element in inner_list:
                inner_result.extend(_inner_helper(element, inner_key, []))
        return inner_result

    result = _inner_helper(obj, key, [])
    if not is_predict_one:
        return result

    if len(result) == 0:
        raise ValueError(f"value of key='{key}' is not found.")
    if len(result) > 1:
        raise ValueError(f"values of key='{key}' are multiple found.")
    return result[0]


def to_jst(gmt: datetime) -> datetime:
    jst = gmt + timedelta(hours=9)
    return jst