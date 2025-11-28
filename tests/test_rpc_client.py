"""
LSY IoT Adapter Hub SDK - RPC Client 测试

测试 AdapterHubRpcClient 的基本功能。
"""

import pytest

from lsyiot_adapter_hub_sdk import AdapterHubRpcClient, AdapterHubRpcResult, AdapterHubRpcError


# RPC 服务器地址
RPC_SERVER_URL = "http://localhost:9030"


class TestAdapterHubRpcClient:
    """AdapterHubRpcClient 测试类"""

    @pytest.fixture
    def client(self):
        """创建 RPC 客户端实例"""
        return AdapterHubRpcClient(RPC_SERVER_URL)

    def test_client_initialization(self, client):
        """测试客户端初始化"""
        assert client.rpc_url == RPC_SERVER_URL
        assert client.client is not None

    def test_topic_message_with_string_data(self, client):
        """测试发送字符串消息"""
        try:
            result = client.topic_message("test/topic", "test message")
            assert isinstance(result, AdapterHubRpcResult)
            assert result.code == 200
            assert result.is_success is True
        except AdapterHubRpcError as e:
            # 如果服务器未运行，跳过测试
            if e.code == -1001:
                pytest.skip(f"RPC 服务器未运行: {RPC_SERVER_URL}")
            raise

    def test_topic_message_with_dict_data(self, client):
        """测试发送字典消息"""
        try:
            data = {"device_id": "test_device_001", "temperature": 25.5, "humidity": 60.0, "timestamp": 1732780800}
            result = client.topic_message("sensor/data", data)
            assert isinstance(result, AdapterHubRpcResult)
            assert result.code == 200
            assert result.is_success is True
        except AdapterHubRpcError as e:
            if e.code == -1001:
                pytest.skip(f"RPC 服务器未运行: {RPC_SERVER_URL}")
            raise

    def test_topic_message_with_list_data(self, client):
        """测试发送列表消息"""
        try:
            data = [{"id": 1, "value": 10}, {"id": 2, "value": 20}, {"id": 3, "value": 30}]
            result = client.topic_message("batch/data", data)
            assert isinstance(result, AdapterHubRpcResult)
            assert result.code == 200
            assert result.is_success is True
        except AdapterHubRpcError as e:
            if e.code == -1001:
                pytest.skip(f"RPC 服务器未运行: {RPC_SERVER_URL}")
            raise

    def test_connection_error(self):
        """测试连接错误"""
        # 使用一个无效的地址来测试连接错误
        invalid_client = AdapterHubRpcClient("http://localhost:59999")

        with pytest.raises(AdapterHubRpcError) as exc_info:
            invalid_client.topic_message("test/topic", "test")

        assert exc_info.value.code == -1001
        assert "连接失败" in exc_info.value.message


class TestAdapterHubRpcResult:
    """AdapterHubRpcResult 测试类"""

    def test_result_from_success_response(self):
        """测试成功响应的解析"""
        json_str = '{"code": 200, "message": "成功", "data": null, "error": false}'
        result = AdapterHubRpcResult(json_str)

        assert result.code == 200
        assert result.message == "成功"
        assert result.data is None
        assert result.error is False
        assert result.is_success is True

    def test_result_from_error_response(self):
        """测试错误响应的解析"""
        json_str = '{"code": -1, "message": "no adapter found for topic test", "data": null, "error": true}'
        result = AdapterHubRpcResult(json_str)

        assert result.code == -1
        assert result.message == "no adapter found for topic test"
        assert result.data is None
        assert result.error is True
        assert result.is_success is False

    def test_result_with_data(self):
        """测试带数据的响应解析"""
        json_str = '{"code": 200, "message": "成功", "data": {"count": 10}, "error": false}'
        result = AdapterHubRpcResult(json_str)

        assert result.code == 200
        assert result.data == {"count": 10}
        assert result.is_success is True

    def test_result_get_method(self):
        """测试 get 方法"""
        json_str = '{"code": 200, "message": "成功", "data": null, "error": false, "extra": "value"}'
        result = AdapterHubRpcResult(json_str)

        assert result.get("code") == 200
        assert result.get("extra") == "value"
        assert result.get("nonexistent") is None
        assert result.get("nonexistent", "default") == "default"

    def test_result_to_dict(self):
        """测试 to_dict 方法"""
        json_str = '{"code": 200, "message": "成功", "data": null, "error": false}'
        result = AdapterHubRpcResult(json_str)

        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert result_dict["code"] == 200
        assert result_dict["message"] == "成功"

    def test_result_raw_property(self):
        """测试 raw 属性"""
        json_str = '{"code": 200, "message": "成功", "data": null, "error": false}'
        result = AdapterHubRpcResult(json_str)

        assert result.raw == json_str

    def test_result_repr(self):
        """测试 __repr__ 方法"""
        json_str = '{"code": 200, "message": "成功", "data": null, "error": false}'
        result = AdapterHubRpcResult(json_str)

        repr_str = repr(result)
        assert "AdapterHubRpcResult" in repr_str
        assert "code=200" in repr_str
        assert "成功" in repr_str


class TestAdapterHubRpcError:
    """AdapterHubRpcError 测试类"""

    def test_error_initialization(self):
        """测试异常初始化"""
        error = AdapterHubRpcError(message="测试错误", code=-1, data={"key": "value"})

        assert error.message == "测试错误"
        assert error.code == -1
        assert error.data == {"key": "value"}

    def test_error_str(self):
        """测试异常字符串表示"""
        error = AdapterHubRpcError(message="测试错误", code=-1001)

        error_str = str(error)
        assert "[Code -1001]" in error_str
        assert "测试错误" in error_str

    def test_error_raise_and_catch(self):
        """测试异常抛出和捕获"""
        with pytest.raises(AdapterHubRpcError) as exc_info:
            raise AdapterHubRpcError(message="连接失败", code=-1001, data=None)

        assert exc_info.value.code == -1001
        assert exc_info.value.message == "连接失败"
