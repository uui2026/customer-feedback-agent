"""
知识库 API 路由
提供知识库文章的 CRUD 接口
"""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/api/knowledge", tags=["知识库管理"])


# ---- 请求模型 ----

class KnowledgeCreateRequest(BaseModel):
    """知识库文章创建请求"""
    title: str
    content: str
    category: str = ""
    keywords: list = []


class KnowledgeUpdateRequest(BaseModel):
    """知识库文章更新请求"""
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    keywords: Optional[list] = None


# ---- 固定路径接口（必须在动态路由之前） ----

@router.get("/", summary="获取知识库文章列表")
async def list_articles(
    category: Optional[str] = Query(None, description="按分类筛选"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """获取知识库文章列表"""
    articles = await KnowledgeService.get_all(db, category, skip, limit)
    return [
        {
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "category": a.category,
            "keywords": a.keywords,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in articles
    ]


@router.get("/categories", summary="获取知识库分类列表")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """获取所有知识库分类"""
    from sqlalchemy import select, func
    from backend.models.knowledge import KnowledgeArticle
    result = await db.execute(
        select(KnowledgeArticle.category, func.count(KnowledgeArticle.id))
        .group_by(KnowledgeArticle.category)
    )
    return [{"name": row[0], "count": row[1]} for row in result.all() if row[0]]


@router.get("/search/{keyword}", summary="搜索知识库")
async def search_articles(keyword: str, db: AsyncSession = Depends(get_db)):
    """按关键词搜索知识库文章"""
    articles = await KnowledgeService.search(db, keyword)
    return [
        {
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "category": a.category,
            "keywords": a.keywords,
        }
        for a in articles
    ]


@router.post("/", summary="创建知识库文章")
async def create_article(request: KnowledgeCreateRequest, db: AsyncSession = Depends(get_db)):
    """创建知识库文章"""
    article = await KnowledgeService.create(db, request.model_dump())
    return {
        "id": article.id,
        "message": "文章创建成功",
    }


# ---- 动态路由（放在固定路径之后） ----

@router.get("/{article_id}", summary="获取文章详情")
async def get_article(article_id: int, db: AsyncSession = Depends(get_db)):
    """根据ID获取文章详情"""
    article = await KnowledgeService.get_by_id(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    return {
        "id": article.id,
        "title": article.title,
        "content": article.content,
        "category": article.category,
        "keywords": article.keywords,
        "created_at": article.created_at.isoformat() if article.created_at else None,
    }


@router.put("/{article_id}", summary="更新文章")
async def update_article(
    article_id: int,
    request: KnowledgeUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """更新文章"""
    update_data = request.model_dump(exclude_unset=True)
    article = await KnowledgeService.update(db, article_id, update_data)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    return {"id": article.id, "message": "文章更新成功"}


@router.delete("/{article_id}", summary="删除文章")
async def delete_article(article_id: int, db: AsyncSession = Depends(get_db)):
    """删除文章"""
    success = await KnowledgeService.delete(db, article_id)
    if not success:
        raise HTTPException(status_code=404, detail="文章不存在")
    return {"message": "文章删除成功"}
