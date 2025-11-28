"""
LSY IoT Adapter Hub SDK - RPC Result

RPC 响应结果类定义。
"""

import json
from typing import Dict, Any, Optional


class AdapterHubRpcResult:
    """Adapter Hub RPC 响应结果类"""

    def __init__(self, result: str):
        """初始化 RPC 响应结果

        Args:
            result: RPC 返回的 JSON 字符串
        """
        self._raw_result = result
        self._json_result = json.loads(result)

    def get(self, key: str, default: Any = None) -> Any:
        """从结果字典中获取值

        Args:
            key: 键名
            default: 默认值

        Returns:
            对应键的值，如果不存在则返回默认值
        """
        return self._json_result.get(key, default)

    @property
    def code(self) -> int:
        """获取状态码

        Returns:
            状态码，200 表示成功，其他表示失败
        """
        return self._json_result.get("code", -1)

    @property
    def message(self) -> str:
        """获取状态消息

        Returns:
            状态消息
        """
        return self._json_result.get("message", "Unknown error")

    @property
    def data(self) -> Optional[Any]:
        """获取返回数据

        Returns:
            返回数据，可能为 None
        """
        return self._json_result.get("data")

    @property
    def error(self) -> bool:
        """是否有错误

        Returns:
            True 表示有错误，False 表示成功
        """
        return self._json_result.get("error", True)

    @property
    def is_success(self) -> bool:
        """是否成功

        Returns:
            True 表示成功，False 表示失败
        """
        return self.code == 200 and not self.error

    @property
    def raw(self) -> str:
        """获取原始 JSON 字符串

        Returns:
            原始 JSON 字符串
        """
        return self._raw_result

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典

        Returns:
            解析后的字典
        """
        return self._json_result.copy()

    def __repr__(self) -> str:
        return f"AdapterHubRpcResult(code={self.code}, message='{self.message}', error={self.error})"
