from dotenv import load_dotenv

load_dotenv()

1.项目用途是：根据知识库回答的智能客服系统，用于第三方客服系统调用。python版本是3.122.项目结构用 A：简洁分层3.数据库PostgreSQL,认证授权后面进行讨论，配置管理使用Pydantic，不需要任务列表，api文档使用内置的FastAPI文档，暂不需要部署相关4.需要日志配置。需要全局异常处理中间件，需要单元测试，需要请求验证/限流。需要cors配置，允许所有来源的请求
