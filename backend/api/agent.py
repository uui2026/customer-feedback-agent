"""
智能体编排 API 路由
提供智能体流水线处理和分析报告接口
"""

import json
from pydantic import BaseModel
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.agents.orchestrator import AgentOrchestrator
from backend.services.feedback_service import FeedbackService
from backend.services.ticket_service import TicketService
from backend.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/api/agent", tags=["智能体编排"])

# 编排器实例
orchestrator = AgentOrchestrator()


# ---- 请求模型 ----

class ProcessFeedbackRequest(BaseModel):
    """处理单条反馈请求"""
    content: str
    channel: str = "manual"
    customer_name: str = ""
    customer_contact: str = ""


class ProcessBatchRequest(BaseModel):
    """批量处理请求"""
    items: List[dict]


# ---- 接口定义 ----

@router.get("/pipeline/status", summary="获取流水线状态")
async def get_pipeline_status():
    """获取智能体流水线的运行状态"""
    return {
        "status": "ready",
        "agents": [
            {"name": "data_collector", "status": "idle", "description": "数据采集智能体"},
            {"name": "intent_analyzer", "status": "idle", "description": "意图分析智能体"},
            {"name": "ticket_router", "status": "idle", "description": "工单路由智能体"},
            {"name": "reply_generator", "status": "idle", "description": "回复生成智能体"},
            {"name": "review_analyzer", "status": "idle", "description": "复盘分析智能体"},
        ],
        "last_run": None,
        "total_processed": 0,
    }


@router.post("/pipeline/run", summary="运行完整流水线")
async def run_full_pipeline(db: AsyncSession = Depends(get_db)):
    """
    运行完整的智能体流水线
    数据采集 → 意图分析 → 工单路由 → 回复生成
    """
    # 获取知识库
    kb_data = await KnowledgeService.get_all_as_dicts(db)

    # 执行采集和处理
    result = orchestrator.collect_and_process(kb_data)

    # 持久化所有结果
    saved_count = 0
    for item in result["results"]:
        if "error" in item:
            continue

        fb_data = item["feedback"]

        # 创建反馈记录
        feedback_record = await FeedbackService.create(db, {
            "channel": fb_data.get("channel", "unknown"),
            "content": fb_data.get("content", ""),
            "customer_name": fb_data.get("customer_name", ""),
            "customer_contact": fb_data.get("customer_contact", ""),
            "intent": fb_data.get("intent"),
            "sentiment": fb_data.get("sentiment"),
            "tags": fb_data.get("tags", []),
            "status": "processing",
        })

        # 创建工单
        ticket_info = item.get("ticket")
        if ticket_info:
            await TicketService.create(db, {
                "feedback_id": feedback_record.id,
                "team": ticket_info["team"],
                "priority": ticket_info["priority"],
                "sla_deadline": ticket_info["sla_deadline"],
                "assigned_to": ticket_info["assigned_to"],
                "status": "open",
            })

        saved_count += 1

    return {
        "message": f"采集 {result['collected']} 条，成功处理并入库 {saved_count} 条",
        "collected": result["collected"],
        "processed": saved_count,
        "results": result["results"],
    }


@router.post("/data-collector/run", summary="运行数据采集智能体")
async def run_data_collector(db: AsyncSession = Depends(get_db)):
    """
    运行数据采集智能体
    从所有渠道采集反馈数据
    """
    from backend.agents.data_collector import DataCollectorAgent

    collector = DataCollectorAgent()
    all_feedback = collector.collect_all()

    created_count = 0
    created_items = []

    for fb in all_feedback:
        feedback_data = {
            "channel": fb.channel,
            "content": fb.content,
            "customer_name": fb.customer_name,
            "customer_contact": fb.customer_contact,
            "status": "pending",
        }

        feedback = await FeedbackService.create(db, feedback_data)
        created_count += 1
        created_items.append({
            "id": feedback.id,
            "channel": fb.channel,
        })

    return {
        "message": f"成功采集并入库 {created_count} 条反馈",
        "count": created_count,
        "items": created_items,
    }


@router.post("/intent-analyzer/run", summary="运行意图分析智能体")
async def run_intent_analyzer(
    feedback_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    运行意图分析智能体
    对指定反馈进行意图分析
    """
    from backend.agents.intent_analyzer import IntentAnalyzerAgent

    feedback = await FeedbackService.get_by_id(db, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈记录不存在")

    analyzer = IntentAnalyzerAgent()
    analysis = analyzer.analyze(feedback.content)

    # 更新反馈记录
    await FeedbackService.update(db, feedback_id, {
        "intent": analysis["intent"],
        "sentiment": analysis["sentiment"],
        "tags": analysis["tags"],
        "status": "analyzed",
    })

    return {
        "feedback_id": feedback_id,
        "analysis": analysis,
        "message": "意图分析完成",
    }


@router.post("/ticket-router/run", summary="运行工单路由智能体")
async def run_ticket_router(
    feedback_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    运行工单路由智能体
    根据反馈内容进行工单路由
    """
    from backend.agents.ticket_router import TicketRouterAgent

    feedback = await FeedbackService.get_by_id(db, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈记录不存在")

    # 获取团队数据
    from backend.models.team import Team
    from sqlalchemy import select
    result = await db.execute(select(Team))
    teams = result.scalars().all()

    router_agent = TicketRouterAgent()
    routing = router_agent.route(
        feedback.content,
        feedback.intent,
        feedback.tags,
        [t.__dict__ for t in teams]
    )

    # 创建工单
    ticket = await TicketService.create(db, {
        "feedback_id": feedback_id,
        "team": routing["team"],
        "priority": routing["priority"],
        "sla_deadline": routing["sla_deadline"],
        "assigned_to": routing["assigned_to"],
        "status": "open",
    })

    # 更新反馈状态
    await FeedbackService.update(db, feedback_id, {"status": "routed"})

    return {
        "feedback_id": feedback_id,
        "ticket_id": ticket.id,
        "routing": routing,
        "message": "工单路由完成",
    }


@router.post("/reply-generator/run", summary="运行回复生成智能体")
async def run_reply_generator(
    feedback_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    运行回复生成智能体
    基于知识库生成回复
    """
    from backend.agents.reply_generator import ReplyGeneratorAgent

    feedback = await FeedbackService.get_by_id(db, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈记录不存在")

    # 获取知识库
    kb_data = await KnowledgeService.get_all_as_dicts(db)

    generator = ReplyGeneratorAgent()
    reply = generator.generate(
        feedback.content,
        feedback.intent,
        feedback.sentiment,
        kb_data
    )

    # 更新反馈记录
    await FeedbackService.update(db, feedback_id, {
        "generated_reply": reply["content"],
        "status": "replied",
    })

    return {
        "feedback_id": feedback_id,
        "reply": reply,
        "message": "回复生成完成",
    }


@router.get("/status", summary="获取所有智能体状态")
async def get_all_agents_status():
    """获取所有智能体的运行状态"""
    return {
        "agents": [
            {
                "name": "data_collector",
                "display_name": "数据采集智能体",
                "status": "idle",
                "last_run": None,
                "processed_count": 0,
            },
            {
                "name": "intent_analyzer",
                "display_name": "意图分析智能体",
                "status": "idle",
                "last_run": None,
                "processed_count": 0,
            },
            {
                "name": "ticket_router",
                "display_name": "工单路由智能体",
                "status": "idle",
                "last_run": None,
                "processed_count": 0,
            },
            {
                "name": "reply_generator",
                "display_name": "回复生成智能体",
                "status": "idle",
                "last_run": None,
                "processed_count": 0,
            },
            {
                "name": "review_analyzer",
                "display_name": "复盘分析智能体",
                "status": "idle",
                "last_run": None,
                "processed_count": 0,
            },
        ],
    }


@router.get("/logs", summary="获取智能体运行日志")
async def get_agent_logs(
    agent_name: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """获取智能体的运行日志"""
    # 这里可以实现日志记录和查询
    # 目前返回模拟数据
    return {
        "logs": [
            {
                "id": 1,
                "agent": "system",
                "action": "system_start",
                "message": "系统启动完成",
                "timestamp": "2026-01-01T00:00:00",
            }
        ],
        "total": 1,
    }


@router.post("/process", summary="处理单条反馈")
async def process_single_feedback(
    request: ProcessFeedbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    使用完整智能体流水线处理单条反馈
    Pipeline: 意图分析 → 工单路由 → 回复生成
    """
    # 获取知识库
    kb_data = await KnowledgeService.get_all_as_dicts(db)

    # 准备反馈数据
    feedback_data = {
        "content": request.content,
        "channel": request.channel,
        "customer_name": request.customer_name,
        "customer_contact": request.customer_contact,
    }

    # 执行流水线处理
    result = orchestrator.process_feedback(feedback_data, kb_data)

    # 持久化 - 创建反馈记录
    fb_data = result["feedback"]
    feedback_record = await FeedbackService.create(db, {
        "channel": fb_data.get("channel", "manual"),
        "content": fb_data.get("content", ""),
        "customer_name": fb_data.get("customer_name", ""),
        "customer_contact": fb_data.get("customer_contact", ""),
        "intent": fb_data.get("intent"),
        "sentiment": fb_data.get("sentiment"),
        "tags": fb_data.get("tags", []),
        "status": "processing",
    })

    # 持久化 - 创建工单
    ticket_info = result["ticket"]
    ticket_record = await TicketService.create(db, {
        "feedback_id": feedback_record.id,
        "team": ticket_info["team"],
        "priority": ticket_info["priority"],
        "sla_deadline": ticket_info["sla_deadline"],
        "assigned_to": ticket_info["assigned_to"],
        "status": "open",
    })

    return {
        "feedback_id": feedback_record.id,
        "ticket_id": ticket_record.id,
        "analysis": {
            "intent": fb_data.get("intent"),
            "sentiment": fb_data.get("sentiment"),
            "tags": fb_data.get("tags"),
        },
        "routing": ticket_info,
        "reply": result["reply"],
        "message": "反馈处理完成",
    }


@router.post("/analyze", summary="仅进行意图分析")
async def analyze_only(request: ProcessFeedbackRequest):
    """
    仅执行意图分析，不创建工单
    用于前端预览分析结果
    """
    from backend.agents.intent_analyzer import IntentAnalyzerAgent

    analyzer = IntentAnalyzerAgent()
    result = analyzer.analyze(request.content)

    return {
        "intent": result["intent"],
        "sentiment": result["sentiment"],
        "tags": result["tags"],
    }


@router.get("/report", summary="生成反馈分析报告")
async def generate_report(db: AsyncSession = Depends(get_db)):
    """
    基于历史反馈数据生成分析报告
    包括趋势分析、热门问题、优化建议等
    """
    # 获取所有反馈数据
    feedbacks = await FeedbackService.get_all_as_dicts(db)

    # 生成分析报告
    report = orchestrator.generate_analysis_report(feedbacks)

    return report
