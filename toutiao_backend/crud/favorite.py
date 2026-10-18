from sqlalchemy import select, func, join, delete
from sqlalchemy.ext.asyncio import AsyncSession
from modules import favorite
from modules.news import News


async def is_favourite(
        db: AsyncSession, news_id: int,user_id:int
):
    stmt = select(favorite.Favorite).where(favorite.Favorite.news_id == news_id, favorite.Favorite.user_id == user_id)
    result = await db.execute(stmt)
    if (result.scalar_one_or_none()):
        return True
    else:
        return False


async def add_new_favorite(
        db:AsyncSession,
        user_id:int,
        news_id:int
):
    # 先查重：连点、多标签页提交时会重复 POST，直接插入会撞 user_news_unique 唯一约束
    if await is_favourite(db, news_id, user_id):
        return None
    fav = favorite.Favorite(news_id=news_id, user_id=user_id)
    db.add(fav)
    await db.commit()
    await db.refresh(fav)
    return fav


# 删除收藏
async def remove_favorite(
        db:AsyncSession,
        user_id:int,
        news_id:int
):
    stmt = delete(favorite.Favorite).where(
        favorite.Favorite.news_id == news_id,
        favorite.Favorite.user_id == user_id
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


# 获取收藏列表
async def get_favorite_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10
):
    # 查询总数
    count_query = select (func.count()).where(favorite.Favorite.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    # 查询收藏列表  联表查询 join() + 收藏时间排序 + 分页
    # select(查询主体模型类，字段别名).join(联合查询的模型类，联合查询的条件).where().order_by().offset().limit()
    # 别名：Favorite.create_at.label("favorite_time")
    offset = (page -1) * page_size

    # offset: 跳过多少条数据，limit：最多返回多少条数据，用于分页查询
    # join: 联合查询，将两个模型类连接起来
    # in: 在某个范围内

# 重点：select 筛选的是列，join、where、order_by、offset、limit 筛选的是行

    # (新闻对象，收藏时间，收藏 id)
    query = (select(News,favorite.Favorite.created_at.label("favorite_time"),favorite.Favorite.id.label("favorite_id"))
    .join(favorite.Favorite,favorite.Favorite.news_id == News.id)
    .where(favorite.Favorite.user_id == user_id)
    .order_by(favorite.Favorite.created_at.desc())
    .offset(offset)
    .limit(page_size))

    result = await db.execute(query)
    rows = result.all()
    return rows,total


async def remove_all_favorites(
        db:AsyncSession,
        user_id:int
):
    stmt = delete(favorite.Favorite).where(favorite.Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0