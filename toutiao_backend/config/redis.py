import json
import os

import redis.asyncio as redis

from config import ENV_FILE  # noqa: F401  触发 .env 加载

# 读环境变量，没有就取默认值
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD") or None

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True,
    socket_connect_timeout=3,
    socket_timeout=3,
)

async def get_cache(key:str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败: {e}")
        return None


# 读取：列表或字典
async def get_json_cache(key:str):
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"获取JSON缓存失败: {e}")
        return None

# 设置缓存
async def set_cache(key:str, value, expire:int = 3600):
    try:
        if isinstance(value,(dict,list)):   # 检查 value 是否是字典或列表类型
            value = json.dumps(value,ensure_ascii=False)    # 把 Python 对象序列化成 JSON 格式的字符串
        await redis_client.setex(key,expire,value)
        return True
    except Exception as e:
        print(f"设置缓存失败: {e}")
        return False