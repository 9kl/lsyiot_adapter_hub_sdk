"""
LSY IoT Adapter Hub SDK - RPC Client

基于 rpcserver.py 中 TopicMessageRpcServer 的定义实现的客户端 SDK，
用于向 Adapter Hub 发送主题消息。
"""

import json
from typing import Dict, Union, List
from xmlrpc.client import ServerProxy, Fault, ProtocolError
from http.client import RemoteDisconnected
from socket import error as SocketError

from .exceptions import AdapterHubRpcError
from .rpc_result import AdapterHubRpcResult


class AdapterHubRpcClient:
    """Adapter Hub RPC Client SDK - 用于向 Adapter Hub 发送主题消息"""

    def __init__(self, rpc_server_url: str):
        """初始化 RPC 客户端

        Args:
            rpc_server_url: RPC 服务器地址，例如 'http://localhost:8080/rpc'
        """
        self.rpc_url = rpc_server_url
        self.client = ServerProxy(rpc_server_url, allow_none=True)

    def _parse_response(self, response: str) -> AdapterHubRpcResult:
        """解析 RPC 响应

        Args:
            response: RPC 返回的 JSON 字符串

        Returns:
            AdapterHubRpcResult 响应结果对象

        Raises:
            AdapterHubRpcError: 当 RPC 调用返回错误时（code != 200）
        """
        result = AdapterHubRpcResult(response)
        if not result.is_success:
            raise AdapterHubRpcError(message=result.message, code=result.code, data=result.data)
        return result

    def _call_rpc(self, method_name: str, *args) -> AdapterHubRpcResult:
        """统一的 RPC 调用方法，处理各种连接异常

        Args:
            method_name: RPC 方法名
            *args: RPC 方法参数

        Returns:
            AdapterHubRpcResult 响应结果对象

        Raises:
            AdapterHubRpcError: 当 RPC 调用失败时（包括连接异常、服务端异常等）
        """
        try:
            method = getattr(self.client, method_name)
            response = method(*args)
            return self._parse_response(response)
        except AdapterHubRpcError:
            # _parse_response 抛出的业务逻辑错误，直接向上传递
            raise
        except Fault as e:
            # XMLRPC 服务端返回的错误
            raise AdapterHubRpcError(message=f"RPC 服务端错误: {e.faultString}", code=e.faultCode, data=None)
        except ProtocolError as e:
            # HTTP 协议错误（如 404, 500 等）
            raise AdapterHubRpcError(message=f"RPC 协议错误: {e.errcode} {e.errmsg}", code=-1000, data={"url": e.url, "errcode": e.errcode, "errmsg": e.errmsg})
        except TimeoutError as e:
            # 连接超时（必须在 OSError 之前捕获，因为 TimeoutError 是 OSError 的子类）
            raise AdapterHubRpcError(message=f"RPC 连接超时: {self.rpc_url}", code=-1002, data={"url": self.rpc_url, "error": str(e)})
        except (ConnectionRefusedError, RemoteDisconnected, SocketError, OSError) as e:
            # 连接被拒绝、远程断开、socket 错误和其他 OSError
            raise AdapterHubRpcError(message=f"RPC 连接失败: 无法连接到服务器 {self.rpc_url} - {str(e)}", code=-1001, data={"url": self.rpc_url, "error": str(e)})
        except json.JSONDecodeError as e:
            # JSON 解析失败
            raise AdapterHubRpcError(message="RPC 响应解析失败: 服务端返回的不是有效的 JSON 格式", code=-1003, data={"error": str(e)})
        except Exception as e:
            # 其他未预期的错误
            raise AdapterHubRpcError(message=f"RPC 调用异常: {type(e).__name__} - {str(e)}", code=-1999, data={"error_type": type(e).__name__, "error": str(e)})

    def topic_message(
        self,
        topic: str,
        data: Union[str, Dict, List],
    ) -> AdapterHubRpcResult:
        """发送主题消息到 Adapter Hub

        根据配置的规则，将消息路由到对应的适配器进行解析和转发。

        Args:
            topic: 主题名称，用于匹配规则中配置的 topic
            data: 消息数据，可以是以下类型：
                - str: 原始字符串数据
                - Dict: 字典数据，会自动序列化为 JSON
                - List: 列表数据，会自动序列化为 JSON

        Returns:
            AdapterHubRpcResult 响应结果对象，包含以下属性：
                - code: 状态码，200 表示成功
                - message: 状态消息
                - data: 返回数据
                - error: 是否有错误
                - is_success: 是否成功

        Raises:
            AdapterHubRpcError: 当 RPC 调用失败时，可能的错误包括：
                - 找不到对应 topic 的适配器
                - 适配器解析消息失败
                - 网络连接错误
                - 服务端处理异常

        Example:
            >>> client = AdapterHubRpcClient("http://localhost:8080/rpc")
            >>> # 发送字符串消息
            >>> result = client.topic_message("sensor/temperature", "25.5")
            >>> print(result.is_success)  # True
            >>> print(result.message)     # "成功"
            >>> # 发送字典消息
            >>> result = client.topic_message("device/status", {"device_id": "001", "status": "online"})
            >>> # 发送列表消息
            >>> result = client.topic_message("batch/data", [{"id": 1}, {"id": 2}])
        """
        return self._call_rpc("topic_message", topic, data)
