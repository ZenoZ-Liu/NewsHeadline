from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class FavoriteCheckResponse(BaseModel):
    is_favorite: bool =Field(...,alias="isFavorite",description="是否收藏")

class FavoriteAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId", description="新闻ID")

class NewsItemBase(BaseModel):
    id:int
    title:str
    description:Optional[str] =None
    image: Optional[str] =None
    author: Optional[str] = None
    category_id : int =Field(alias= "categoryId")
    views:int
    publish_time:Optional[datetime] =Field(None,alias= "publishTime")

    model_config = ConfigDict(
        from_attributes=True,   # 必须设置为 True，否则 NewsItemBase.model_validate(item) 无法从 ORM 对象取值
        populate_by_name=True,  # 必须：category_id / publish_time 配了驼峰别名，开启后校验时才会按字段名去 ORM 对象上取值
    )

class FavoriteNewsItemResponse(NewsItemBase):
    favorite_id: int=Field(...,alias="favoriteId",description="收藏ID")
    favorite_time: datetime = Field(...,alias="favoriteTime")

    model_config = ConfigDict(
        populate_by_name=True,  # 允许使用别名字段名
        from_attributes=True,   # 可以接受字典以外类型的数据
    )

class FavoriteListResponse(BaseModel):
    list: list[FavoriteNewsItemResponse]
    total:int
    has_more: bool = Field(..., alias="hasMore", description="是否有更多数据")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )