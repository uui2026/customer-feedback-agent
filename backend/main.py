"""
FastAPI 应用入口
多渠道客户反馈智能处理系统 - 后端服务
"""

import json
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import init_db, close_db


# ---- 应用生命周期管理 ----

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期事件"""
    # 启动时：初始化数据库
    print("🚀 正在启动多渠道客户反馈智能处理系统...")
    await init_db()
    await _init_knowledge_base()
    await _init_teams()
    print("✅ 系统启动完成！")
    print(f"📖 API 文档: http://localhost:8000/docs")
    print(f"📊 仪表盘: http://localhost:8000/api/dashboard/stats")

    yield

    # 关闭时：清理资源
    await close_db()
    print("👋 系统已关闭")


# ---- 创建 FastAPI 应用 ----

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="多渠道客户反馈闭环处理系统 - 5个AI智能体协作",
    lifespan=lifespan,
)

# ---- CORS 中间件 ----

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- 注册路由 ----

from backend.api.feedback import router as feedback_router
from backend.api.ticket import router as ticket_router
from backend.api.dashboard import router as dashboard_router
from backend.api.knowledge import router as knowledge_router
from backend.api.agent import router as agent_router

app.include_router(feedback_router)
app.include_router(ticket_router)
app.include_router(dashboard_router)
app.include_router(knowledge_router)
app.include_router(agent_router)


# ---- 根路由 ----

@app.get("/", tags=["系统"])
async def root():
    """系统首页"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "多渠道客户反馈闭环处理系统",
        "agents": [
            "数据采集智能体 (DataCollector)",
            "意图分析智能体 (IntentAnalyzer)",
            "工单路由智能体 (TicketRouter)",
            "回复生成智能体 (ReplyGenerator)",
            "评论分析智能体 (ReviewAnalyzer)",
        ],
        "channels": ["企业微信 (WeCom)", "抖音 (Douyin)", "邮件 (Email)"],
        "docs": "/docs",
    }


@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查"""
    return {"status": "healthy", "version": settings.app_version}


# ---- 辅助函数 ----

async def _init_knowledge_base():
    """
    初始化知识库 - 从 faq.json 加载数据到数据库
    仅在数据库为空时执行
    """
    from backend.database import async_session_factory
    from backend.services.knowledge_service import KnowledgeService

    async with async_session_factory() as db:
        count = await KnowledgeService.count(db)
        if count > 0:
            print(f"📚 知识库已有 {count} 条记录，跳过初始化")
            return

        # 读取 FAQ 文件
        faq_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "backend", "knowledge_base", "faq.json"
        )
        if not os.path.exists(faq_path):
            # 尝试备用路径
            faq_path = os.path.join(
                os.path.dirname(__file__),
                "knowledge_base", "faq.json"
            )

        if not os.path.exists(faq_path):
            print("⚠️  未找到 faq.json 文件，跳过知识库初始化")
            return

        with open(faq_path, "r", encoding="utf-8") as f:
            faq_data = json.load(f)

        for item in faq_data:
            await KnowledgeService.create(db, {
                "title": item.get("title", ""),
                "content": item.get("content", ""),
                "category": item.get("category", ""),
                "keywords": item.get("keywords", []),
            })

        await db.commit()
        print(f"📚 知识库初始化完成，加载 {len(faq_data)} 条 FAQ")


async def _init_teams():
    """
    初始化团队数据
    将配置中的团队信息写入数据库
    """
    from backend.database import async_session_factory
    from sqlalchemy import select, func
    from backend.models.team import Team

    async with async_session_factory() as db:
        result = await db.execute(select(func.count(Team.id)))
        count = result.scalar()
        if count > 0:
            print(f"👥 团队数据已有 {count} 条，跳过初始化")
            return

        for team_name, team_config in settings.teams.items():
            import json as json_mod
            team = Team(
                name=team_name,
                description=team_config["description"],
                keywords=json_mod.dumps(team_config["keywords"], ensure_ascii=False),
                member_count=team_config["member_count"],
            )
            db.add(team)

        await db.commit()
        print(f"👥 团队数据初始化完成，共 {len(settings.teams)} 个团队")


# ---- 启动入口 ----

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
