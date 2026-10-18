
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from config.db_conf import get_db
from crud import history
from modules.users import User
from schemas.history import HistoryAddRequest, HistoryListResponse
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/history", tags=["history"])


# 添加浏览记录
@router.post("/add")
async def add_history(
        data:HistoryAddRequest,
        db:AsyncSession = Depends(get_db),
        user:User = Depends(get_current_user),
):
    # add_history 内部已经处理了“存在则更新时间、不存在则插入”，调一次就够了
    result = await history.add_history(db,user.id,data.news_id)
    return success_response(message="添加浏览记录成功", data=result)


# 获取浏览记录列表
@router.get("/list")
async def get_history_list(
        db:AsyncSession = Depends(get_db),
        user:User = Depends(get_current_user),
        page:int = Query(default=1, ge=1),
        page_size:int = Query(default=10, ge=1, le=100, alias="pageSize")
):
    rows,total = await history.get_history_list(db,user.id,page,page_size)
    # rows 每一项是 (新闻对象, 浏览时间, 历史记录 ID)
    history_list = [
        {
            **news.__dict__,
            "view_time": view_time,
            "history_id": history_id
        }for news,view_time,history_id in rows
    ]
    has_more = total > page * page_size
    data = HistoryListResponse(list=history_list,total=total,has_more=has_more)
    return success_response(message="获取浏览记录列表成功", data=data)

@router.delete("/delete/{news_id}")
async def delete_history(
        news_id:int,
        db:AsyncSession = Depends(get_db),
        user:User = Depends(get_current_user)
):
    result = await history.delete_history(db,user.id,news_id)
    if not result:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="浏览记录不存在")
    return success_response(message="删除浏览记录成功")

@router.delete("/clear")
async def clear_history(
        db:AsyncSession = Depends(get_db),
        user:User = Depends(get_current_user)
):
    count = await history.clear_history(db,user.id)
    return success_response(message=f"清空{count}条历史记录")
