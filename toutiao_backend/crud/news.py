from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from crud.news_cache import set_cache_categories, get_cache_news_list, set_cache_news_list, set_cache_news_detail, \
    get_cache_related_news, set_cache_related_news, get_cached_categories, get_cache_news_detail
from modules import news
from schemas.favorite import NewsItemBase


# 获取新闻分类
async def get_categories(db:AsyncSession,skip:int =0,limit:int =10):
    # 先尝试从缓存中读取数据
    cached_categories = await get_cached_categories()
    if cached_categories is not None:
        return cached_categories

    stmt =select(news.Categories).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()
    # 写入缓存
    if categories is not None:
        categories = jsonable_encoder(categories)
        await set_cache_categories(categories)

    # 返回数据
    return categories


# 获取新闻列表
async def get_news_list(
        db:AsyncSession,
        category_id:int,
        skip:int =0,
        limit:int =10
):
    # 先尝试从缓存获取数据
    page = (skip // limit) +1
    cached_list = await get_cache_news_list(category_id,page,limit)
    if cached_list is not None:
        # 要的是 ORM, 但是缓存中存的是字典，需要将字典转换为 ORM 对象
        return [news.News(**item) for item in cached_list]


    stmt = select(news.News).where(news.News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()

    # 写入缓存
    if news_list is not None:
        # 这一步相当于“过滤”，将 item 中不用的字段去掉(比如 created_at 等)，只保留 NewsItemBase 中定义的字段
        news_data = [
            # mode="json": 把 datetime 转成 JSON 字符串；by_alias=False: 保留 category_id / publish_time 原始字段名，
            # 因为缓存命中时要还原成 News(**item)，用的必须是模型字段名，而不是驼峰别名
            NewsItemBase.model_validate(item).model_dump(mode="json",by_alias=False)
            for item in news_list
        ]
        await set_cache_news_list(category_id,page,limit,news_data)
    return news_list

# 获取新闻总数
async def get_news_count(
        db:AsyncSession,
        category_id:int
):
    stmt = select(func.count(news.News.id)).where(news.News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()

# 获取新闻详情
async def get_news_detail(
        db:AsyncSession,
        news_id:int
):
    # 先从缓存中获取
    cached_detail = await get_cache_news_detail(news_id)
    if cached_detail is not None:
        return news.News(**cached_detail)

    stmt = select(news.News).where(news.News.id == news_id)
    result = await db.execute(stmt)
    news_d = result.scalar_one_or_none()

    if news_d:
        news_detail = jsonable_encoder(news_d)
        await set_cache_news_detail(news_id, news_detail)
    return news_d


# 新闻浏览量+1
async def increase_news_views(db:AsyncSession,news_id:int):
    stmt = update(news.News).where(news.News.id == news_id).values(views=news.News.views + 1)
    result = await db.execute(stmt)
    await db.commit()

    # 提交后回查数据库里的真实值：命中详情缓存时，news_detail 是用缓存还原出来的临时对象（不在 Session 里），
    # 上面的 UPDATE 不会同步它的 views，直接读对象属性会比数据库少 1（表现为刷新后浏览量不涨甚至倒退）。
    new_views = (await db.execute(
        select(news.News.views).where(news.News.id == news_id)
    )).scalar_one_or_none()
    return result.rowcount > 0, new_views


# 获取相关推荐新闻
async def get_related_news(
        db:AsyncSession,
        category_id:int,
        news_id:int,
        limit:int =5
):
    # 先从缓存中获取
    cached_related = await get_cache_related_news(news_id, category_id)
    if cached_related is not None:
        # 直接返回缓存中的数据，缓存中存的是字典
        return cached_related

    # 查询数据库
    stmt =(
        select(news.News)
        .where(
            news.News.id != news_id,
            news.News.category_id == category_id
        )
        .order_by(
            news.News.views.desc(),
            news.News.publish_time.desc()
        )
        .limit(limit)
    )

    result = await db.execute(stmt)
    related_news = result.scalars().all()

    related_list =[
        {
            "id": item.id,
            "title": item.title,
            "content": item.content,
            "image": item.image,
            "author": item.author,
            "publish_time": item.publish_time,
            "views": item.views,
            "category_id": item.category_id
        }
        for item in related_news
    ]

    # 写入缓存
    if related_list is not None:
        # publish_time 是 datetime，直接 json.dumps 会报 “not JSON serializable”，先编码一次
        await set_cache_related_news(news_id, category_id, jsonable_encoder(related_list))

    return related_news
