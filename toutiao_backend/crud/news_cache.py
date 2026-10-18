from typing import List, Dict, Any, Optional

from config.redis import get_json_cache, set_cache

CATEGORIES_KEY = "news:categories"
NEWS_LIST_PREFIX = "news_list:"
NEWS_DETAIL_PREFIX = "news_detail:"
RELATED_NEWS_PREFIX = "related_news:"

# 读取缓存-新闻分类
async def get_cached_categories():
    return await get_json_cache(CATEGORIES_KEY)

# 写入缓存-新闻分类 key = news:categories + 分类数据 + 过期时间
async def set_cache_categories(data:List[Dict[str,Any]], expire=7200):
    return await set_cache(CATEGORIES_KEY,data,expire)

#写入缓存-新闻列表 key = news_list:分类id:页码:每页数量  + 列表数据 + 过期时间
async def set_cache_news_list(category_id:Optional[int],page:int,size:int,news_list:List[Dict[str,Any]], expire=1800):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
    return await set_cache(key,news_list,expire)

# 读取缓存-新闻列表 key = news_list:分类id:页码:每页数量
async def get_cache_news_list(category_id:Optional[int],page:int,size:int):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
    return await get_json_cache(key)

# 读取缓存-新闻详情 key = news:detail:新闻id
async def get_cache_news_detail(news_id: int):
    key = f"{NEWS_DETAIL_PREFIX}{news_id}"
    return await get_json_cache(key)

# 写入缓存-新闻详情 key = news:detail:新闻id + 新闻详情 + 过期时间
async def set_cache_news_detail(news_id: int, news_detail: Dict[str, Any], expire=1800):
    key = f"{NEWS_DETAIL_PREFIX}{news_id}"
    return await set_cache(key, news_detail, expire)

# 写入缓存-相关新闻 key = news:related:新闻id:分类id + 相关新闻列表 + 过期时间
async def set_cache_related_news(news_id: int, category_id: int, related_list: List[Dict[str, Any]], expire=1800):
    key = f"{RELATED_NEWS_PREFIX}{news_id}:{category_id}"
    return await set_cache(key, related_list, expire)

# 读取缓存-相关新闻 key = news:related:新闻id:分类id
async def get_cache_related_news(news_id: int, category_id: int):
    key = f"{RELATED_NEWS_PREFIX}{news_id}:{category_id}"
    return await get_json_cache(key)