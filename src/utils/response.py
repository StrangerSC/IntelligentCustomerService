from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse


class UnifiedResponse(JSONResponse):
    """
    统一响应封装类

    用于规范全站 API 的返回结构，确保前后端交互具备一致的契约格式：
    {
        "code": <业务状态码>,
        "message": <提示信息>,
        "data": <业务数据>
    }

    使用方式：
        - 成功场景：return UnifiedResponse.success(data={...})
        - 异常场景：return UnifiedResponse.error(message="参数错误", code=400)
    """

    def __init__(
        self,
        data: Any = None,
        code: int = 200,
        message: str = "success",
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        构造统一响应对象

        参数说明：
            data: 业务层待返回的数据载体，支持任意可序列化类型，默认为 None
            code: 业务状态码，与 HTTP 状态解耦，便于前端做精细化状态判断，默认 200
            message: 面向用户或前端的可读性说明，默认 "success"
            status_code: HTTP 协议层状态码，默认 200
            headers: 需要额外注入的响应头，例如链路追踪 ID、限流标识等，可选
        """
        content = {
            "code": code,
            "message": message,
            "data": data,
        }
        super().__init__(content=content, status_code=status_code, headers=headers)

    @staticmethod
    def success(data: Any = None, message: str = "success") -> "UnifiedResponse":
        """
        构造成功响应

        参数说明：
            data: 业务数据载荷，默认 None
            message: 成功提示文案，默认 "success"

        返回：
            UnifiedResponse 实例，HTTP 状态码固定为 200
        """
        return UnifiedResponse(data=data, message=message)

    @staticmethod
    def error(
        message: str = "error", code: int = 500, status_code: int = 500
    ) -> "UnifiedResponse":
        """
        构造异常/错误响应

        参数说明：
            message: 错误描述信息，建议清晰明了，便于问题定位，默认 "error"
            code: 业务异常编码，默认 500
            status_code: HTTP 层错误状态码，默认 500

        返回：
            UnifiedResponse 实例，data 字段固定为 None
        """
        return UnifiedResponse(
            data=None, code=code, message=message, status_code=status_code
        )