"""
仪表盘 API 路由
提供系统总览统计和 SLA 合规情况
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.services.feedback_service import FeedbackService
from backend.services.ticket_service import TicketService

router = APIRouter(prefix="/api/dashboard", tags=["仪表盘"])


@router.get("/stats", summary="获取仪表盘统计数据")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """
    获取系统总览统计

    返回:
        total_feedback: 反馈总数
        by_channel: 按渠道统计
        by_intent: 按意图统计
        by_status: 按状态统计
        by_sentiment: 按情感统计
        total_tickets: 工单总数
        ticket_stats: 工单统计
        sla_compliance: SLA 合规情况
    """
    # 反馈统计
    total_feedback = await FeedbackService.count(db)
    by_channel = await FeedbackService.count_by_field(db, "channel")
    by_intent = await FeedbackService.count_by_field(db, "intent")
    by_status = await FeedbackService.count_by_field(db, "status")
    by_sentiment = await FeedbackService.count_by_field(db, "sentiment")

    # 工单统计
    total_tickets = await TicketService.count(db)
    ticket_by_team = await TicketService.count_by_field(db, "team")
    ticket_by_status = await TicketService.count_by_field(db, "status")
    ticket_by_priority = await TicketService.count_by_field(db, "priority")

    # SLA 合规情况
    sla_info = await TicketService.check_sla_compliance(db)

    return {
        "total_feedback": total_feedback,
        "by_channel": by_channel,
        "by_intent": by_intent,
        "by_status": by_status,
        "by_sentiment": by_sentiment,
        "total_tickets": total_tickets,
        "ticket_by_team": ticket_by_team,
        "ticket_by_status": ticket_by_status,
        "ticket_by_priority": ticket_by_priority,
        "sla_compliance": sla_info,
    }


@router.get("/recent", summary="获取最近反馈")
@router.get("/recent-feedback", summary="获取最近反馈")
async def get_recent_feedbacks(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """获取最近的反馈列表"""
    feedbacks = await FeedbackService.get_all(db, limit=limit)
    return [
        {
            "id": fb.id,
            "channel": fb.channel,
            "content": fb.content[:100] + "..." if len(fb.content or "") > 100 else fb.content,
            "customer_name": fb.customer_name,
            "intent": fb.intent,
            "sentiment": fb.sentiment,
            "status": fb.status,
            "created_at": fb.created_at.isoformat() if fb.created_at else None,
        }
        for fb in feedbacks
    ]


@router.get("/channels", summary="获取渠道分布")
async def get_channel_distribution(db: AsyncSession = Depends(get_db)):
    """获取各渠道的反馈分布"""
    channel_stats = await FeedbackService.count_by_field(db, "channel")
    channel_names = {"wecom": "企业微信", "douyin": "抖音", "email": "邮件"}
    return [
        {"name": channel_names.get(k, k), "value": v}
        for k, v in channel_stats.items()
    ]


@router.get("/intents", summary="获取意图分布")
async def get_intent_distribution(db: AsyncSession = Depends(get_db)):
    """获取各意图的反馈分布"""
    intent_stats = await FeedbackService.count_by_field(db, "intent")
    intent_names = {"inquiry": "咨询", "complaint": "投诉", "suggestion": "建议"}
    return [
        {"name": intent_names.get(k, k), "value": v}
        for k, v in intent_stats.items()
    ]


@router.get("/sentiments", summary="获取情感分布")
async def get_sentiment_distribution(db: AsyncSession = Depends(get_db)):
    """获取各情感的反馈分布"""
    sentiment_stats = await FeedbackService.count_by_field(db, "sentiment")
    sentiment_names = {"positive": "正面", "negative": "负面", "neutral": "中性"}
    return [
        {"name": sentiment_names.get(k, k), "value": v}
        for k, v in sentiment_stats.items()
    ]


@router.get("/trends", summary="获取趋势数据")
async def get_trend_data(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
):
    """获取指定天数的趋势数据"""
    from datetime import datetime, timedelta
    from sqlalchemy import func
    from backend.models.feedback import Feedback

    # 获取最近N天每天的反馈数量
    start_date = datetime.now() - timedelta(days=days)
    result = await db.execute(
        select(
            func.date(Feedback.created_at).label('date'),
            func.count().label('count')
        )
        .filter(Feedback.created_at >= start_date)
        .group_by(func.date(Feedback.created_at))
        .order_by(func.date(Feedback.created_at))
    )
    rows = result.all()

    # 填充缺失日期
    trends = []
    current_date = start_date.date()
    end_date = datetime.now().date()
    data_dict = {row.date: row.count for row in rows}

    while current_date <= end_date:
        date_str = current_date.isoformat()
        trends.append({
            "date": date_str,
            "count": data_dict.get(date_str, 0)
        })
        current_date += timedelta(days=1)

    return trends


@router.get("/sla-alerts", summary="获取SLA预警")
async def get_sla_alerts(db: AsyncSession = Depends(get_db)):
    """获取SLA即将超时的工单预警"""
    from datetime import datetime

    tickets = await TicketService.get_all(db)
    alerts = []
    now = datetime.now()

    for ticket in tickets:
        if ticket.sla_deadline and ticket.status not in ["resolved", "closed"]:
            remaining = (ticket.sla_deadline - now).total_seconds() / 3600
            if 0 < remaining < 2:  # 2小时内超时
                alerts.append({
                    "id": ticket.id,
                    "ticket_id": ticket.id,
                    "team": ticket.team,
                    "remaining_hours": round(remaining, 1),
                    "sla_deadline": ticket.sla_deadline.isoformat(),
                })

    return alerts
