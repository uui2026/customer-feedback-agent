"""
客户反馈 ORM 模型
记录从各渠道收集到的客户反馈信息，包含意图、情感、标签等分析结果
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer
from backend.database import Base


class Feedback(Base):
    """客户反馈表"""
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 渠道来源: wecom(企业微信), douyin(抖音), email(邮件)
    channel = Column(String(20), nullable=False, comment="反馈渠道")
    # 反馈内容
    content = Column(Text, nullable=False, comment="反馈内容")
    # 客户姓名
    customer_name = Column(String(100), nullable=True, comment="客户姓名")
    # 客户联系方式
    customer_contact = Column(String(100), nullable=True, comment="客户联系方式")
    # 意图分类: inquiry(咨询), complaint(投诉), suggestion(建议)
    intent = Column(String(20), nullable=True, comment="意图分类")
    # 情感倾向: positive(正面), negative(负面), neutral(中性)
    sentiment = Column(String(20), nullable=True, comment="情感倾向")
    # 标签列表，JSON 格式存储，如 ["退款", "售后"]
    tags = Column(String(500), nullable=True, comment="标签列表(JSON)")
    # 处理状态: pending(待处理), processing(处理中), resolved(已解决), closed(已关闭)
    status = Column(String(20), default="pending", comment="处理状态")
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    # 更新时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def __repr__(self):
        return f"<Feedback(id={self.id}, channel={self.channel}, intent={self.intent})>"
