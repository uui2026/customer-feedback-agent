"""
数据库连接模块
使用 SQLAlchemy 2.0 异步引擎 + aiosqlite 驱动
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from backend.config import settings


# 创建异步数据库引擎
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False},  # SQLite 需要此配置
)

# 创建异步会话工厂
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """ORM 基类"""
    pass


async def get_db() -> AsyncSession:
    """获取数据库会话的依赖注入函数"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库 - 创建所有表"""
    async with engine.begin() as conn:
        # 导入所有模型以确保注册到 Base.metadata
        from backend.models import feedback, ticket, knowledge, team  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)
    print("✅ 数据库表初始化完成")


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()
    print("🔒 数据库连接已关闭")
