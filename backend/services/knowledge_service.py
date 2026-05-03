"""
知识库服务
提供知识库文章的 CRUD 操作
"""

import json
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.knowledge import KnowledgeArticle


class KnowledgeService:
    """知识库数据服务类"""

    @staticmethod
    async def create(db: AsyncSession, data: dict) -> KnowledgeArticle:
        """
        创建知识库文章

        参数:
            db: 数据库会话
            data: 文章数据字典

        返回:
            创建的 KnowledgeArticle 对象
        """
        keywords = data.get("keywords", [])
        if isinstance(keywords, list):
            keywords = json.dumps(keywords, ensure_ascii=False)

        article = KnowledgeArticle(
            title=data.get("title", ""),
            content=data.get("content", ""),
            category=data.get("category", ""),
            keywords=keywords,
            created_at=datetime.now(),
        )
        db.add(article)
        await db.flush()
        await db.refresh(article)
        return article

    @staticmethod
    async def get_by_id(db: AsyncSession, article_id: int) -> Optional[KnowledgeArticle]:
        """根据ID查询文章"""
        result = await db.execute(
            select(KnowledgeArticle).where(KnowledgeArticle.id == article_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[KnowledgeArticle]:
        """查询文章列表，支持按分类筛选"""
        query = select(KnowledgeArticle)

        if category:
            query = query.where(KnowledgeArticle.category == category)

        query = query.order_by(KnowledgeArticle.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update(db: AsyncSession, article_id: int, data: dict) -> Optional[KnowledgeArticle]:
        """更新文章"""
        article = await KnowledgeService.get_by_id(db, article_id)
        if not article:
            return None

        if "title" in data:
            article.title = data["title"]
        if "content" in data:
            article.content = data["content"]
        if "category" in data:
            article.category = data["category"]
        if "keywords" in data:
            keywords = data["keywords"]
            if isinstance(keywords, list):
                keywords = json.dumps(keywords, ensure_ascii=False)
            article.keywords = keywords

        await db.flush()
        await db.refresh(article)
        return article

    @staticmethod
    async def delete(db: AsyncSession, article_id: int) -> bool:
        """删除文章"""
        article = await KnowledgeService.get_by_id(db, article_id)
        if not article:
            return False
        await db.delete(article)
        await db.flush()
        return True

    @staticmethod
    async def get_all_as_dicts(db: AsyncSession) -> List[dict]:
        """获取所有文章为字典列表"""
        articles = await KnowledgeService.get_all(db)
        return [
            {
                "id": a.id,
                "title": a.title,
                "content": a.content,
                "category": a.category,
                "keywords": a.keywords,
                "created_at": a.created_at,
            }
            for a in articles
        ]

    @staticmethod
    async def search(db: AsyncSession, keyword: str) -> List[KnowledgeArticle]:
        """
        按关键词搜索文章
        匹配标题、内容、关键词字段
        """
        query = select(KnowledgeArticle).where(
            KnowledgeArticle.title.contains(keyword)
            | KnowledgeArticle.content.contains(keyword)
            | KnowledgeArticle.keywords.contains(keyword)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def count(db: AsyncSession) -> int:
        """统计文章总数"""
        result = await db.execute(select(func.count(KnowledgeArticle.id)))
        return result.scalar()
