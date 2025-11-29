"""
LSY IoT Adapter Hub SDK - API Result

API 响应结果类定义。
"""

import json
from typing import Dict, Any


class AdapterHubApiResult:
    """Adapter Hub API 响应结果类"""

    def __init__(self, response_text: str, status_code: int):
        """初始化 API 响应结果

        Args:
            response_text: API 返回的响应文本（JSON 字符串）
            status_code: HTTP 状态码
        """
        self._raw_result = response_text
        self._status_code = status_code
        self._json_result = json.loads(response_text)

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
    def status(self) -> str:
        """获取状态字符串

        Returns:
            状态字符串，'success' 或 'error'
        """
        return self._json_result.get("status", "error")

    @property
    def message(self) -> str:
        """获取状态消息

        Returns:
            状态消息
        """
        return self._json_result.get("message", "Unknown error")

    @property
    def status_code(self) -> int:
        """获取 HTTP 状态码

        Returns:
            HTTP 状态码
        """
        return self._status_code

    @property
    def is_success(self) -> bool:
        """是否成功

        Returns:
            True 表示成功，False 表示失败
        """
        return self._status_code == 200 and self.status == "success"

    @property
    def raw(self) -> str:
        """获取原始响应文本

        Returns:
            原始响应文本
        """
        return self._raw_result

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典

        Returns:
            解析后的字典
        """
        return self._json_result.copy()

    def __repr__(self) -> str:
        return f"AdapterHubApiResult(status='{self.status}', message='{self.message}', status_code={self.status_code})"
