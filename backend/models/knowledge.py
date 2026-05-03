"""
知识库文章 ORM 模型
存储常见问题解答（FAQ）和业务知识，供回复生成智能体检索匹配
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer
from backend.database import Base


class KnowledgeArticle(Base):
    """知识库文章表"""
    __tablename__ = "knowledge_articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 文章标题
    title = Column(String(200), nullable=False, comment="文章标题")
    # 文章内容
    content = Column(Text, nullable=False, comment="文章内容")
    # 分类: 退款, 售后, 技术, 活动, 账号 等
    category = Column(String(50), nullable=True, comment="文章分类")
    # 关键词列表，JSON 格式存储，用于检索匹配
    keywords = Column(String(500), nullable=True, comment="关键词(JSON)")
    # 创建时间
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    def __repr__(self):
        return f"<KnowledgeArticle(id={self.id}, title={self.title})>"
