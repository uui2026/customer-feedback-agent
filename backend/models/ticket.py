"""
工单 ORM 模型
由路由智能体根据反馈意图和优先级自动分配到对应团队
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer
from backend.database import Base


class Ticket(Base):
    """工单表"""
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 关联的反馈 ID
    feedback_id = Column(Integer, nullable=False, comment="关联反馈ID")
    # 分配的团队: 客服组, 技术组, 产品组, 运营组
    team = Column(String(50), nullable=False, comment="处理团队")
    # 优先级: high(高), medium(中), low(低)
    priority = Column(String(10), default="medium", comment="优先级")
    # SLA 截止时间
    sla_deadline = Column(DateTime, nullable=True, comment="SLA截止时间")
    # 工单状态: open(待处理), in_progress(处理中), resolved(已解决), closed(已关闭), overdue(已超时)
    status = Column(String(20), default="open", comment="工单状态")
    # 指派处理人
    assigned_to = Column(String(100), nullable=True, comment="指派处理人")
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def __repr__(self):
        return f"<Ticket(id={self.id}, team={self.team}, status={self.status})>"
