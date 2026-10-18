import os

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from config import ENV_FILE  # noqa: F401  触发 .env 加载


def _build_database_url() -> URL | str:
    """优先使用 DATABASE_URL 整串配置，否则由分项变量拼装。

    用 URL.create() 而不是手工拼字符串，密码里出现 @ : / % 等字符时
    由 SQLAlchemy 负责转义，避免连接串被解析错位。
    """
    explicit_url = os.getenv("DATABASE_URL", "").strip()
    if explicit_url:
        return explicit_url

    return URL.create(
        drivername="mysql+aiomysql",
        username=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        database=os.getenv("MYSQL_DATABASE", "news_app"),
        query={"charset": os.getenv("MYSQL_CHARSET", "utf8mb4")},
    )


ASYNC_DATABASE_URL = _build_database_url()

# 创建异步引擎（此时不会建立真实连接，首次查询才连接）
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() in {"1", "true", "yes"},
    pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
    pool_pre_ping=True,
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# 依赖项
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
