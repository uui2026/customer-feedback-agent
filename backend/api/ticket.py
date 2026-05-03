"""
工单 API 路由
提供工单的 CRUD 接口和状态更新接口
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.services.ticket_service import TicketService

router = APIRouter(prefix="/api/tickets", tags=["工单管理"])


# ---- 请求/响应模型 ----

class TicketCreateRequest(BaseModel):
    """工单创建请求"""
    feedback_id: int
    team: str = "客服组"
    priority: str = "medium"
    assigned_to: Optional[str] = None


class TicketUpdateStatusRequest(BaseModel):
    """工单状态更新请求"""
    status: str
    assigned_to: Optional[str] = None


# ---- 接口定义 ----

@router.get("/", summary="获取工单列表")
async def list_tickets(
    team: Optional[str] = Query(None, description="按团队筛选"),
    status: Optional[str] = Query(None, description="按状态筛选"),
    priority: Optional[str] = Query(None, description="按优先级筛选"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """获取工单列表"""
    tickets = await TicketService.get_all(db, team, status, priority, skip, limit)
    return [
        {
            "id": t.id,
            "feedback_id": t.feedback_id,
            "team": t.team,
            "priority": t.priority,
            "sla_deadline": t.sla_deadline.isoformat() if t.sla_deadline else None,
            "status": t.status,
            "assigned_to": t.assigned_to,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        }
        for t in tickets
    ]


@router.get("/{ticket_id}", summary="获取工单详情")
async def get_ticket(ticket_id: int, db: AsyncSession = Depends(get_db)):
    """根据ID获取工单详情"""
    ticket = await TicketService.get_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="工单不存在")

    return {
        "id": ticket.id,
        "feedback_id": ticket.feedback_id,
        "team": ticket.team,
        "priority": ticket.priority,
        "sla_deadline": ticket.sla_deadline.isoformat() if ticket.sla_deadline else None,
        "status": ticket.status,
        "assigned_to": ticket.assigned_to,
        "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
        "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None,
    }


@router.post("/", summary="创建工单")
async def create_ticket(request: TicketCreateRequest, db: AsyncSession = Depends(get_db)):
    """手动创建工单"""
    from backend.config import settings

    # 计算 SLA 截止时间（默认按咨询类 24小时）
    from datetime import timedelta
    sla_hours = settings.sla_hours.get("inquiry", 24)
    sla_deadline = datetime.now() + timedelta(hours=sla_hours)

    ticket_data = {
        "feedback_id": request.feedback_id,
        "team": request.team,
        "priority": request.priority,
        "sla_deadline": sla_deadline,
        "assigned_to": request.assigned_to or "待分配",
        "status": "open",
    }

    ticket = await TicketService.create(db, ticket_data)
    return {
        "id": ticket.id,
        "message": "工单创建成功",
    }


@router.put("/{ticket_id}/status", summary="更新工单状态")
async def update_ticket_status(
    ticket_id: int,
    request: TicketUpdateStatusRequest,
    db: AsyncSession = Depends(get_db),
):
    """更新工单状态"""
    ticket = await TicketService.update_status(db, ticket_id, request.status, request.assigned_to)
    if not ticket:
        raise HTTPException(status_code=404, detail="工单不存在")
    return {
        "id": ticket.id,
        "status": ticket.status,
        "assigned_to": ticket.assigned_to,
        "message": "工单状态更新成功",
    }


@router.delete("/{ticket_id}", summary="删除工单")
async def delete_ticket(ticket_id: int, db: AsyncSession = Depends(get_db)):
    """删除工单"""
    success = await TicketService.delete(db, ticket_id)
    if not success:
        raise HTTPException(status_code=404, detail="工单不存在")
    return {"message": "工单删除成功"}
