from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import get_db
from crud import news

router = APIRouter(prefix="/api/news", tags=["news"])

@router.get("/categories")
async def get_categories(skip:int =0,limit:int =100,db:AsyncSession = Depends(get_db)):
    categories = await news.get_categories(db=db,skip=skip,limit=limit)
    return {
        "code":200,
        "message": "获取分类成功",
        "data":categories
    }

@router.get("/list")
async def get_news(
        category_id: int = Query(...,alias = "categoryId"),
        page:int =Query(1, ge=1),
        page_size: int =Query(10, ge=1, le=100,alias="pageSize"),
        db:AsyncSession = Depends(get_db)
):
    offset = (page-1)*page_size
    news_list = await news.get_news_list(db,category_id,offset,page_size)
    total = await news.get_news_count(db,category_id)

    # 前端列表项读取的是 publishTime / categoryId（驼峰），而 ORM 对象直接序列化出来是
    # publish_time / category_id，所以这里显式映射一遍，否则列表里的“发布时间”会显示为空。
    # 注意：缓存命中的列表项是 News(**dict) 还原出来的对象，同样支持属性访问，两种来源都适用。
    data_list = [
        {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "image": item.image,
            "author": item.author,
            "publishTime": item.publish_time,
            "categoryId": item.category_id,
            "views": item.views,
        }
        for item in news_list
    ]

    return {
        "code":200,
        "message":"success",
        "data":{
            "list": data_list,
            "total": total
        }

    }

@router.get("/detail")
async def get_news_detail(news_id:int = Query(...,alias="id"),db:AsyncSession = Depends(get_db)):
    news_detail = await news.get_news_detail(db,news_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")

    # 浏览量 +1，并取数据库里的真实值（缓存命中时对象是临时的，不会被自动同步）
    news_res, new_views = await news.increase_news_views(db,news_id)
    if not news_res:
        raise HTTPException(status_code=404, detail="新闻不存在")

    # 新闻详情-相关推荐
    related_news = await news.get_related_news(db,news_detail.category_id,news_detail.id)

    data = {
        "id":news_detail.id,
        "title":news_detail.title,
        "description": news_detail.description,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": new_views,
        "relatedNews": related_news
    }

    return{
        "code":200,
        "message":"success",
        "data":data
    }
