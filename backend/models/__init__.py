"""
数据模型包
导入所有 ORM 模型，确保 SQLAlchemy 能够发现并创建对应表
"""

from backend.models.feedback import Feedback
from backend.models.ticket import Ticket
from backend.models.knowledge import KnowledgeArticle
from backend.models.team import Team

__all__ = ["Feedback", "Ticket", "KnowledgeArticle", "Team"]
