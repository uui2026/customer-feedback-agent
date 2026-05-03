"""
应用配置模块
使用 Pydantic Settings 管理全局配置，包括数据库连接、渠道配置、SLA策略等
"""

from pydantic_settings import BaseSettings
from typing import Dict, List


class Settings(BaseSettings):
    """全局应用配置"""

    # 应用基本信息
    app_name: str = "多渠道客户反馈智能处理系统"
    app_version: str = "1.0.0"
    debug: bool = True

    # 数据库配置 - 使用 SQLite + aiosqlite
    database_url: str = "sqlite+aiosqlite:///./feedback_agent.db"

    # CORS 配置
    cors_origins: List[str] = ["*"]

    # 渠道配置 - 模拟多渠道数据采集
    channels: Dict[str, dict] = {
        "wecom": {
            "name": "企业微信",
            "enabled": True,
            "polling_interval": 60,  # 轮询间隔（秒）
        },
        "douyin": {
            "name": "抖音",
            "enabled": True,
            "polling_interval": 120,
        },
        "email": {
            "name": "邮件",
            "enabled": True,
            "polling_interval": 300,
        },
    }

    # SLA 策略配置（小时）
    sla_hours: Dict[str, int] = {
        "complaint": 4,    # 投诉类：4小时响应
        "inquiry": 24,     # 咨询类：24小时响应
        "suggestion": 72,  # 建议类：72小时响应
    }

    # 团队配置
    teams: Dict[str, dict] = {
        "客服组": {
            "description": "处理客户咨询、投诉、售后服务等",
            "keywords": ["咨询", "投诉", "售后", "退换货", "退款", "服务", "态度", "客服"],
            "member_count": 10,
        },
        "技术组": {
            "description": "处理技术故障、系统问题、功能异常等",
            "keywords": ["bug", "故障", "崩溃", "报错", "技术", "系统", "功能", "无法", "异常", "闪退"],
            "member_count": 8,
        },
        "产品组": {
            "description": "处理产品功能建议、需求反馈、体验优化等",
            "keywords": ["建议", "希望", "功能", "产品", "优化", "改进", "需求", "体验"],
            "member_count": 6,
        },
        "运营组": {
            "description": "处理活动咨询、推广反馈、账号问题等",
            "keywords": ["活动", "优惠", "推广", "账号", "充值", "积分", "会员", "运营"],
            "member_count": 7,
        },
    }

    # 知识库配置
    knowledge_base_path: str = "backend/knowledge_base/faq.json"

    # 日志配置
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置单例
settings = Settings()
