"""
LSY IoT Adapter Hub SDK - API Client

基于 HTTP POST 请求的 API 客户端 SDK，
用于向 Adapter Hub 发送 WEB 请求消息。
"""

import json
from typing import Dict, Any

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError as RequestsConnectionError

from .api_result import AdapterHubApiResult
from .exceptions import AdapterHubApiError


class AdapterHubApiClient:
    """Adapter Hub API Client SDK - 用于向 Adapter Hub 发送 WEB 请求消息"""

    def __init__(self, api_base_url: str, verify_ssl: bool = True, timeout: int = 30):
        """初始化 API 客户端

        Args:
            api_base_url: API 主地址，例如 'http://localhost:8080/api'
            verify_ssl: 是否验证 SSL 证书，默认为 True。设置为 False 可忽略 SSL 验证
            timeout: 请求超时时间（秒），默认为 30 秒
        """
        self.api_base_url = api_base_url.rstrip("/")
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self._session = requests.Session()

    def send_request(self, endpoint: str, data: Dict[str, Any]) -> AdapterHubApiResult:
        """发送 POST 请求到指定端点

        Args:
            endpoint: API 端点路径，例如 '/sensor/data' 或 'sensor/data'
            data: 请求数据字典

        Returns:
            AdapterHubApiResult 响应结果对象，包含以下属性：
                - status: 状态字符串，'success' 或 'error'
                - message: 状态消息
                - is_success: 是否成功
                - status_code: HTTP 状态码

        Raises:
            AdapterHubApiError: 当 API 调用失败时，可能的错误包括：
                - 连接失败
                - 连接超时
                - HTTP 错误
                - JSON 解析失败
                - 服务端返回错误

        Example:
            >>> client = AdapterHubApiClient("http://localhost:8080/api")
            >>> result = client.send_request("/sensor/data", {"temperature": 25.5})
            >>> print(result.is_success)  # True
            >>> print(result.message)     # "Data received successfully"
        """
        # 构建完整 URL
        endpoint = endpoint.lstrip("/")
        url = f"{self.api_base_url}/{endpoint}"

        try:
            response = self._session.post(url, json=data, verify=self.verify_ssl, timeout=self.timeout, headers={"Content-Type": "application/json"})

            # 先检查 HTTP 状态码
            if response.status_code >= 400:
                # HTTP 错误状态码，直接抛出异常
                error_message = self._get_http_error_message(response.status_code)
                raise AdapterHubApiError(
                    message=f"HTTP 错误: {response.status_code} {error_message}",
                    code=response.status_code,
                    data={"url": url, "status_code": response.status_code, "response_text": response.text[:500] if response.text else None},
                )

            # 解析响应
            return self._parse_response(response)

        except AdapterHubApiError:
            # 已经是 AdapterHubApiError，直接向上抛出
            raise
        except Timeout as e:
            raise AdapterHubApiError(message=f"API 请求超时: {url}", code=-1002, data={"url": url, "error": str(e)})
        except RequestsConnectionError as e:
            raise AdapterHubApiError(message=f"API 连接失败: 无法连接到服务器 {url}", code=-1001, data={"url": url, "error": str(e)})
        except RequestException as e:
            raise AdapterHubApiError(message=f"API 请求异常: {str(e)}", code=-1000, data={"url": url, "error": str(e)})
        except Exception as e:
            raise AdapterHubApiError(message=f"API 调用异常: {type(e).__name__} - {str(e)}", code=-1999, data={"error_type": type(e).__name__, "error": str(e)})

    def _parse_response(self, response: requests.Response) -> AdapterHubApiResult:
        """解析 HTTP 响应

        Args:
            response: requests 响应对象

        Returns:
            AdapterHubApiResult 响应结果对象

        Raises:
            AdapterHubApiError: 当响应状态为错误时
        """
        try:
            result = AdapterHubApiResult(response.text, response.status_code)
        except json.JSONDecodeError as e:
            raise AdapterHubApiError(
                message="API 响应解析失败: 服务端返回的不是有效的 JSON 格式", code=-1003, data={"error": str(e), "response_text": response.text[:500] if response.text else None}
            )

        # 检查业务状态是否成功
        if not result.is_success:
            raise AdapterHubApiError(message=result.message, code=result.status_code, data=result.to_dict())

        return result

    def _get_http_error_message(self, status_code: int) -> str:
        """获取 HTTP 状态码对应的错误消息

        Args:
            status_code: HTTP 状态码

        Returns:
            错误消息
        """
        http_errors = {
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            408: "Request Timeout",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable",
            504: "Gateway Timeout",
        }
        return http_errors.get(status_code, "Unknown Error")

    def close(self):
        """关闭客户端会话"""
        self._session.close()

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时关闭会话"""
        self.close()
        return False
