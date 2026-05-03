"""
团队 ORM 模型
定义处理反馈的团队信息，用于智能路由分派
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer
from backend.database import Base


class Team(Base):
    """团队表"""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 团队名称: 客服组, 技术组, 产品组, 运营组
    name = Column(String(50), nullable=False, unique=True, comment="团队名称")
    # 团队描述
    description = Column(Text, nullable=True, comment="团队描述")
    # 关键词列表，JSON 格式存储，用于反馈匹配分派
    keywords = Column(String(500), nullable=True, comment="匹配关键词(JSON)")
    # 团队成员数
    member_count = Column(Integer, default=0, comment="成员数量")
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    def __repr__(self):
        return f"<Team(id={self.id}, name={self.name})>"
