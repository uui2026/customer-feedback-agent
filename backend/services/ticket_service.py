"""
工单数据服务
提供工单的 CRUD 操作和状态管理
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.ticket import Ticket


class TicketService:
    """工单数据服务类"""

    @staticmethod
    async def create(db: AsyncSession, data: dict) -> Ticket:
        """
        创建工单

        参数:
            db: 数据库会话
            data: 工单数据字典

        返回:
            创建的 Ticket 对象
        """
        ticket = Ticket(
            feedback_id=data.get("feedback_id"),
            team=data.get("team", "客服组"),
            priority=data.get("priority", "medium"),
            sla_deadline=data.get("sla_deadline"),
            status=data.get("status", "open"),
            assigned_to=data.get("assigned_to", "待分配"),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.add(ticket)
        await db.flush()
        await db.refresh(ticket)
        return ticket

    @staticmethod
    async def get_by_id(db: AsyncSession, ticket_id: int) -> Optional[Ticket]:
        """根据ID查询工单"""
        result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_feedback_id(db: AsyncSession, feedback_id: int) -> Optional[Ticket]:
        """根据关联的反馈ID查询工单"""
        result = await db.execute(
            select(Ticket).where(Ticket.feedback_id == feedback_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession,
        team: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Ticket]:
        """查询工单列表，支持按团队、状态、优先级筛选"""
        query = select(Ticket)

        if team:
            query = query.where(Ticket.team == team)
        if status:
            query = query.where(Ticket.status == status)
        if priority:
            query = query.where(Ticket.priority == priority)

        query = query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_status(
        db: AsyncSession, ticket_id: int, status: str, assigned_to: Optional[str] = None
    ) -> Optional[Ticket]:
        """更新工单状态"""
        ticket = await TicketService.get_by_id(db, ticket_id)
        if not ticket:
            return None
        ticket.status = status
        if assigned_to:
            ticket.assigned_to = assigned_to
        ticket.updated_at = datetime.now()
        await db.flush()
        await db.refresh(ticket)
        return ticket

    @staticmethod
    async def delete(db: AsyncSession, ticket_id: int) -> bool:
        """删除工单"""
        ticket = await TicketService.get_by_id(db, ticket_id)
        if not ticket:
            return False
        await db.delete(ticket)
        await db.flush()
        return True

    @staticmethod
    async def count(db: AsyncSession) -> int:
        """统计工单总数"""
        result = await db.execute(select(func.count(Ticket.id)))
        return result.scalar()

    @staticmethod
    async def count_by_field(db: AsyncSession, field_name: str) -> dict:
        """按指定字段分组统计"""
        field = getattr(Ticket, field_name, None)
        if not field:
            return {}
        result = await db.execute(
            select(field, func.count(Ticket.id)).group_by(field)
        )
        return {row[0]: row[1] for row in result.all()}

    @staticmethod
    async def check_sla_compliance(db: AsyncSession) -> dict:
        """
        检查 SLA 合规情况
        统计已超时和合规的工单数量
        """
        now = datetime.now()
        # 已超时的工单（状态不是 resolved/closed 且超过了 sla_deadline）
        overdue_result = await db.execute(
            select(func.count(Ticket.id)).where(
                Ticket.sla_deadline < now,
                Ticket.status.notin_(["resolved", "closed"]),
            )
        )
        overdue_count = overdue_result.scalar()

        # 总工单数
        total = await TicketService.count(db)

        # 合规数
        compliance_rate = ((total - overdue_count) / total * 100) if total > 0 else 100

        return {
            "total": total,
            "overdue": overdue_count,
            "compliance_rate": round(compliance_rate, 2),
        }
