# lsyiot_adapter_hub_sdk

LSY IoT Adapter Hub SDK - 用于与 Adapter Hub RPC 服务进行通信的 Python SDK。

## 安装

```bash
pip install lsyiot-adapter-hub-sdk
```

## 快速开始

### 基本用法

```python
from lsyiot_adapter_hub_sdk import AdapterHubRpcClient, AdapterHubRpcError

# 创建客户端
client = AdapterHubRpcClient("http://localhost:8080/rpc")

# 发送主题消息
try:
    result = client.topic_message("sensor/temperature", {"value": 25.5})
    
    if result.is_success:
        print(f"发送成功: {result.message}")
    else:
        print(f"发送失败: {result.message}")
        
except AdapterHubRpcError as e:
    print(f"RPC 错误: {e}")
```

### 发送不同类型的消息

```python
from lsyiot_adapter_hub_sdk import AdapterHubRpcClient

client = AdapterHubRpcClient("http://localhost:8080/rpc")

# 发送字符串消息
result = client.topic_message("sensor/temperature", "25.5")

# 发送字典消息
result = client.topic_message("device/status", {
    "device_id": "001",
    "status": "online",
    "timestamp": 1732780800
})

# 发送列表消息
result = client.topic_message("batch/data", [
    {"id": 1, "value": 10},
    {"id": 2, "value": 20}
])
```

### 使用响应结果

```python
from lsyiot_adapter_hub_sdk import AdapterHubRpcClient

client = AdapterHubRpcClient("http://localhost:8080/rpc")
result = client.topic_message("sensor/temperature", {"value": 25.5})

# 访问响应属性
print(result.code)        # 状态码，200 表示成功
print(result.message)     # 状态消息
print(result.data)        # 返回数据
print(result.error)       # 是否有错误
print(result.is_success)  # 是否成功

# 转换为字典
result_dict = result.to_dict()

# 获取原始 JSON 字符串
raw_json = result.raw
```

### 异常处理

```python
from lsyiot_adapter_hub_sdk import AdapterHubRpcClient, AdapterHubRpcError

client = AdapterHubRpcClient("http://localhost:8080/rpc")

try:
    result = client.topic_message("sensor/temperature", {"value": 25.5})
except AdapterHubRpcError as e:
    print(f"错误码: {e.code}")
    print(f"错误消息: {e.message}")
    print(f"附加数据: {e.data}")
    
    # 根据错误码处理不同类型的错误
    if e.code == -1001:
        print("连接失败，请检查服务器地址")
    elif e.code == -1002:
        print("连接超时")
    elif e.code == -1003:
        print("响应解析失败")
```

## API 参考

### AdapterHubRpcClient

RPC 客户端类，用于与 Adapter Hub 服务通信。

#### 构造函数

```python
AdapterHubRpcClient(rpc_server_url: str)
```

- `rpc_server_url`: RPC 服务器地址，例如 `http://localhost:8080/rpc`

#### 方法

##### topic_message

```python
topic_message(topic: str, data: Union[str, Dict, List]) -> AdapterHubRpcResult
```

发送主题消息到 Adapter Hub。

- `topic`: 主题名称，用于匹配规则中配置的 topic
- `data`: 消息数据，支持字符串、字典或列表

### AdapterHubRpcResult

RPC 响应结果类。

#### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `code` | `int` | 状态码，200 表示成功 |
| `message` | `str` | 状态消息 |
| `data` | `Any` | 返回数据 |
| `error` | `bool` | 是否有错误 |
| `is_success` | `bool` | 是否成功 |
| `raw` | `str` | 原始 JSON 字符串 |

#### 方法

| 方法 | 说明 |
|------|------|
| `get(key, default)` | 从结果字典中获取值 |
| `to_dict()` | 转换为字典 |

### AdapterHubRpcError

RPC 调用异常类。

#### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `code` | `int` | 错误码 |
| `message` | `str` | 错误消息 |
| `data` | `Any` | 附加数据 |

#### 错误码说明

| 错误码 | 说明 |
|--------|------|
| `200` | 成功 |
| `-1` | 业务逻辑错误 |
| `-1000` | HTTP 协议错误 |
| `-1001` | 连接失败 |
| `-1002` | 连接超时 |
| `-1003` | JSON 解析失败 |
| `-1999` | 未知错误 |

## 许可证

MIT License
