from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from modules.users import User
from schemas.favorite import FavoriteCheckResponse, FavoriteAddRequest, FavoriteListResponse
from utils.auth import get_current_user
from utils.response import success_response
from crud import favorite
router = APIRouter(prefix="/api/favorite", tags=["favourite"])

# 检查新闻收藏状态
@router.get("/check")
async def check_favorite(
        news_id: int = Query(..., alias="newsId"),
        user: User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    result = await favorite.is_favourite(db, news_id,user.id)
    return success_response(message="检查收藏状态", data=FavoriteCheckResponse(isFavorite=result))

@router.post("/add")
async def add_favorite(
        data:FavoriteAddRequest,
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)):
    result = await favorite.add_new_favorite(db,user.id,data.news_id)
    if result is None:
        # 已经收藏过：幂等返回，避免前端连点时弹“操作失败”
        return success_response(message="已经收藏过了")
    return success_response(message="添加收藏成功", data=result)

@router.delete("/remove")
async def remove_favorite(
        news_id:int =Query(..., alias="newsId"),
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    result =await favorite.remove_favorite(
        db,
        user.id,
        news_id
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏记录不存在"
        )
    return success_response(message="取消收藏成功")


# 获取收藏列表
@router.get("/list")
async def get_favorite_list(
        page:int = Query(1, ge=1),
        page_size:int = Query(10, ge=1, le=100,alias="pageSize"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    rows,total = await favorite.get_favorite_list(db, user.id, page, page_size)
    # rows 是一个列表，里面每一项是一个元组，元组里面有三个元素：新闻对象、收藏时间、收藏记录ID
    # 单星解包  *：将元组里面的元素拆开，作为函数的参数传入
    # 双星解包 **：将字典里面的键值对拆开，作为关键字参数传入函数
    # news 不是一个字典，而是一个对象，不能直接使用 **news 进行解包，需要将对象转换为字典，可以使用 news.__dict__ 来获取对象的属性字典
    favorite_list =[
        {
            **news.__dict__,
            "favorite_time": favorite_time,
            "favorite_id": favorite_id
        }for news,favorite_time,favorite_id in rows]
    has_more = total > page*page_size

    data = FavoriteListResponse(list = favorite_list, total=total, has_more=has_more)
    return success_response(message="获取收藏列表成功", data=data)


@router.delete("/clear")
async def clear_favorite(
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    count =await favorite.remove_all_favorites(db,user.id)
    return success_response(message=f"清空 {count} 条收藏记录")