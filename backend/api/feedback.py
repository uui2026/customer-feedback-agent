"""
反馈 API 路由
提供反馈数据的 CRUD 接口和批量采集接口
"""

import json
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.services.feedback_service import FeedbackService
from backend.agents.intent_analyzer import IntentAnalyzerAgent

router = APIRouter(prefix="/api/feedbacks", tags=["反馈管理"])


# ---- 请求/响应模型 ----

class FeedbackCreateRequest(BaseModel):
    """反馈创建请求"""
    channel: str
    content: str
    customer_name: str = ""
    customer_contact: str = ""


class FeedbackUpdateStatusRequest(BaseModel):
    """更新反馈状态请求"""
    status: str


class FeedbackResponse(BaseModel):
    """反馈响应"""
    id: int
    channel: str
    content: str
    customer_name: Optional[str]
    customer_contact: Optional[str]
    intent: Optional[str]
    sentiment: Optional[str]
    tags: Optional[str]
    status: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class BatchCollectRequest(BaseModel):
    """批量采集请求"""
    channels: List[str] = ["wecom", "douyin", "email"]


# ---- 意图分析器实例 ----
intent_analyzer = IntentAnalyzerAgent()


# ---- 接口定义 ----

@router.get("/", summary="获取反馈列表")
async def list_feedbacks(
    channel: Optional[str] = Query(None, description="按渠道筛选"),
    intent: Optional[str] = Query(None, description="按意图筛选"),
    status: Optional[str] = Query(None, description="按状态筛选"),
    skip: int = Query(0, ge=0, description="跳过条数"),
    limit: int = Query(100, ge=1, le=1000, description="返回条数"),
    db: AsyncSession = Depends(get_db),
):
    """获取反馈列表，支持分页和筛选"""
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
            "created_at": fb.created_at.isoformat() if fb.created_at else None,
            "updated_at": fb.updated_at.isoformat() if fb.updated_at else None,
        }
        for fb in feedbacks
    ]


@router.get("/{feedback_id}", summary="获取单条反馈详情")
async def get_feedback(feedback_id: int, db: AsyncSession = Depends(get_db)):
    """根据ID获取反馈详情"""
    feedback = await FeedbackService.get_by_id(db, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈记录不存在")

    # 解析 tags
    tags = feedback.tags
    if tags and isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except (json.JSONDecodeError, TypeError):
            tags = []

    return {
        "id": feedback.id,
        "channel": feedback.channel,
        "content": feedback.content,
        "customer_name": feedback.customer_name,
        "customer_contact": feedback.customer_contact,
        "intent": feedback.intent,
        "sentiment": feedback.sentiment,
        "tags": tags,
        "status": feedback.status,
        "created_at": feedback.created_at.isoformat() if feedback.created_at else None,
        "updated_at": feedback.updated_at.isoformat() if feedback.updated_at else None,
    }


@router.post("/", summary="创建新反馈")
async def create_feedback(request: FeedbackCreateRequest, db: AsyncSession = Depends(get_db)):
    """手动创建一条反馈记录，自动进行意图分析"""
    # 自动进行意图和情感分析
    analysis = intent_analyzer.analyze(request.content)

    feedback_data = {
        "channel": request.channel,
        "content": request.content,
        "customer_name": request.customer_name,
        "customer_contact": request.customer_contact,
        "intent": analysis["intent"],
        "sentiment": analysis["sentiment"],
        "tags": analysis["tags"],
        "status": "pending",
    }

    feedback = await FeedbackService.create(db, feedback_data)
    return {
        "id": feedback.id,
        "message": "反馈创建成功",
        "analysis": analysis,
    }


@router.put("/{feedback_id}/status", summary="更新反馈状态")
async def update_feedback_status(
    feedback_id: int,
    request: FeedbackUpdateStatusRequest,
    db: AsyncSession = Depends(get_db),
):
    """更新反馈的处理状态"""
    feedback = await FeedbackService.update_status(db, feedback_id, request.status)
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈记录不存在")
    return {"id": feedback.id, "status": feedback.status, "message": "状态更新成功"}


@router.delete("/{feedback_id}", summary="删除反馈")
async def delete_feedback(feedback_id: int, db: AsyncSession = Depends(get_db)):
    """删除反馈记录"""
    success = await FeedbackService.delete(db, feedback_id)
    if not success:
        raise HTTPException(status_code=404, detail="反馈记录不存在")
    return {"message": "删除成功"}


@router.post("/collect", summary="从所有渠道批量采集反馈")
async def batch_collect(db: AsyncSession = Depends(get_db)):
    """
    从所有渠道采集反馈并自动入库
    包括：企业微信、抖音、邮件
    """
    from backend.agents.data_collector import DataCollectorAgent

    collector = DataCollectorAgent()
    all_feedback = collector.collect_all()

    created_count = 0
    created_items = []

    for fb in all_feedback:
        # 自动进行意图分析
        analysis = intent_analyzer.analyze(fb.content)

        feedback_data = {
            "channel": fb.channel,
            "content": fb.content,
            "customer_name": fb.customer_name,
            "customer_contact": fb.customer_contact,
            "intent": analysis["intent"],
            "sentiment": analysis["sentiment"],
            "tags": analysis["tags"],
            "status": "pending",
        }

        feedback = await FeedbackService.create(db, feedback_data)
        created_count += 1
        created_items.append({
            "id": feedback.id,
            "channel": fb.channel,
            "intent": analysis["intent"],
            "sentiment": analysis["sentiment"],
        })

    return {
        "message": f"成功采集并入库 {created_count} 条反馈",
        "count": created_count,
        "items": created_items,
    }
