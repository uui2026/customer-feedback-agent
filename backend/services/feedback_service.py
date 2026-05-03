"""
反馈数据服务
提供反馈数据的 CRUD 操作
"""

import json
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.feedback import Feedback


class FeedbackService:
    """反馈数据服务类"""

    @staticmethod
    async def create(db: AsyncSession, data: dict) -> Feedback:
        """
        创建新反馈记录

        参数:
            db: 数据库会话
            data: 反馈数据字典

        返回:
            创建的 Feedback 对象
        """
        # 处理 tags 字段 - 如果是列表则转为JSON字符串
        tags = data.get("tags", [])
        if isinstance(tags, list):
            tags = json.dumps(tags, ensure_ascii=False)

        feedback = Feedback(
            channel=data.get("channel", "unknown"),
            content=data.get("content", ""),
            customer_name=data.get("customer_name", ""),
            customer_contact=data.get("customer_contact", ""),
            intent=data.get("intent"),
            sentiment=data.get("sentiment"),
            tags=tags,
            status=data.get("status", "pending"),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.add(feedback)
        await db.flush()
        await db.refresh(feedback)
        return feedback

    @staticmethod
    async def get_by_id(db: AsyncSession, feedback_id: int) -> Optional[Feedback]:
        """根据ID查询反馈"""
        result = await db.execute(select(Feedback).where(Feedback.id == feedback_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession,
        channel: Optional[str] = None,
        intent: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Feedback]:
        """
        查询反馈列表，支持按渠道、意图、状态筛选
        """
        query = select(Feedback)

        if channel:
            query = query.where(Feedback.channel == channel)
        if intent:
            query = query.where(Feedback.intent == intent)
        if status:
            query = query.where(Feedback.status == status)

        query = query.order_by(Feedback.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_status(db: AsyncSession, feedback_id: int, status: str) -> Optional[Feedback]:
        """更新反馈处理状态"""
        feedback = await FeedbackService.get_by_id(db, feedback_id)
        if not feedback:
            return None
        feedback.status = status
        feedback.updated_at = datetime.now()
        await db.flush()
        await db.refresh(feedback)
        return feedback

    @staticmethod
    async def update(db: AsyncSession, feedback_id: int, data: dict) -> Optional[Feedback]:
        """更新反馈记录"""
        feedback = await FeedbackService.get_by_id(db, feedback_id)
        if not feedback:
            return None

        # 更新字段
        if "channel" in data:
            feedback.channel = data["channel"]
        if "content" in data:
            feedback.content = data["content"]
        if "customer_name" in data:
            feedback.customer_name = data["customer_name"]
        if "customer_contact" in data:
            feedback.customer_contact = data["customer_contact"]
        if "intent" in data:
            feedback.intent = data["intent"]
        if "sentiment" in data:
            feedback.sentiment = data["sentiment"]
        if "tags" in data:
            tags = data["tags"]
            if isinstance(tags, list):
                tags = json.dumps(tags, ensure_ascii=False)
            feedback.tags = tags
        if "status" in data:
            feedback.status = data["status"]
        if "generated_reply" in data:
            feedback.generated_reply = data["generated_reply"]

        feedback.updated_at = datetime.now()
        await db.flush()
        await db.refresh(feedback)
        return feedback

    @staticmethod
    async def update_analysis(
        db: AsyncSession, feedback_id: int, intent: str, sentiment: str, tags: list
    ) -> Optional[Feedback]:
        """更新反馈分析结果"""
        feedback = await FeedbackService.get_by_id(db, feedback_id)
        if not feedback:
            return None
        feedback.intent = intent
        feedback.sentiment = sentiment
        feedback.tags = json.dumps(tags, ensure_ascii=False)
        feedback.updated_at = datetime.now()
        await db.flush()
        await db.refresh(feedback)
        return feedback

    @staticmethod
    async def delete(db: AsyncSession, feedback_id: int) -> bool:
        """删除反馈记录"""
        feedback = await FeedbackService.get_by_id(db, feedback_id)
        if not feedback:
            return False
        await db.delete(feedback)
        await db.flush()
        return True

    @staticmethod
    async def count(db: AsyncSession) -> int:
        """统计反馈总数"""
        result = await db.execute(select(func.count(Feedback.id)))
        return result.scalar()

    @staticmethod
    async def count_by_field(db: AsyncSession, field_name: str) -> dict:
        """按指定字段分组统计"""
        field = getattr(Feedback, field_name, None)
        if not field:
            return {}
        result = await db.execute(
            select(field, func.count(Feedback.id)).group_by(field)
        )
        return {row[0]: row[1] for row in result.all()}

    @staticmethod
    async def get_all_as_dicts(
        db: AsyncSession,
        channel: Optional[str] = None,
        intent: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 1000,
    ) -> List[dict]:
        """获取所有反馈为字典列表（用于分析报告）"""
        feedbacks = await FeedbackService.get_all(db, channel, intent, status, skip, limit)
        return [
            {
                "id": fb.id,
                "channel": fb.channel,
                "content": fb.content,
                "customer_name": fb.customer_name,
                "customer_contact": fb.customer_contact,
                "intent": fb.intent,
                "sentiment": fb.sentiment,
                "tags": fb.tags,
                "status": fb.status,
                "created_at": fb.created_at,
                "updated_at": fb.updated_at,
            }
            for fb in feedbacks
        ]
