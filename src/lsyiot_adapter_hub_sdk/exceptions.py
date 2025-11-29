class AdapterHubRpcError(Exception):
    """Adapter Hub RPC 调用异常"""

    def __init__(self, message: str, code: int = -1, data=None):
        """初始化 RPC 异常

        Args:
            message: 错误消息
            code: 错误代码
            data: 附加数据
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.data = data

    def __str__(self):
        return f"[Code {self.code}] {self.message}"


class AdapterHubApiError(Exception):
    """Adapter Hub API 调用异常"""

    def __init__(self, message: str, code: int = -1, data=None):
        """初始化 API 异常

        Args:
            message: 错误消息
            code: 错误代码（HTTP 状态码或自定义错误码）
            data: 附加数据
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.data = data

    def __str__(self):
        return f"[Code {self.code}] {self.message}"
