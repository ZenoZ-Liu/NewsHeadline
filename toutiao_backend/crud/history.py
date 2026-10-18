from datetime import datetime

from sqlalchemy import select, func,delete
from sqlalchemy.ext.asyncio import AsyncSession

from modules import history
from modules.news import News


async def add_history(
        db:AsyncSession,
        user_id:int,
        news_id:int
):
    # 检查是否已经存在历史记录
    query = select(history.History).where(
        history.History.user_id == user_id,
        history.History.news_id == news_id
    )
    result = await db.execute(query)
    existing_history = result.scalar_one_or_none()

    if existing_history:
        # 如果历史记录已存在，更新访问时间
        existing_history.view_time = datetime.now()
        await db.commit()
        return existing_history

    # 如果历史记录不存在，创建新的历史记录
    new_history = history.History(user_id=user_id, news_id=news_id)
    db.add(new_history)
    await db.commit()
    await db.refresh(new_history)
    return new_history


async def get_history_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10
):
    '''
    获取用户浏览记录列表
    '''
    offset = (page - 1) * page_size

    count_query = select(func.count(history.History.id)).where(history.History.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    query = (select(News,history.History.view_time.label("view_time"),history.History.id.label("history_id"))
                    .join(history.History, history.History.news_id == News.id)
                    .where(history.History.user_id == user_id)
                    .order_by(history.History.view_time.desc())
                    .offset(offset)
                    .limit(page_size))

    result = await db.execute(query)
    rows = result.all()
    return rows,total


# 删除历史记录
async def delete_history(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    stmt = delete(history.History).where(
        history.History.user_id == user_id,
        history.History.news_id == news_id
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def clear_history(
        db: AsyncSession,
        user_id: int
):
    stmt = delete(history.History).where(
        history.History.user_id == user_id
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0
