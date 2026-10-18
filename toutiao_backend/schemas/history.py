from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

class NewsItemBase(BaseModel):
    id:int
    title:str
    description:Optional[str] =None
    image: Optional[str] =None
    author: Optional[str] = None
    category_id : int =Field(alias= "categoryId")
    views:int
    publish_time:Optional[datetime] =Field(None,alias= "publishTime")

class HistoryAddRequest(BaseModel):
    news_id:int=Field(...,alias="newsId",description="新闻ID")

class HistoryNewsItemResponse(NewsItemBase):
    """
    浏览历史列表中的新闻项响应
    """
    history_id: int = Field(alias="historyId")
    view_time: datetime = Field(alias="viewTime")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )


class HistoryListResponse(BaseModel):
    list: list[HistoryNewsItemResponse]
    total: int
    has_more: bool = Field(alias="hasMore")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )