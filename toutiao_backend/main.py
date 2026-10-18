from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import news, users, favorite, history
from utils.exception_handlers import register_exception_handlers

app = FastAPI(
    title="NewsHeadline API",
    description="新闻资讯应用后端服务，提供新闻浏览、用户认证、收藏与浏览历史接口。",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # 设置允许访问的源
    allow_credentials=True, # 允许携带 Cookie
    allow_methods=["*"],    # 允许所有请求方式
    allow_headers=["*"],    # 允许所有请求
)

# 注册异常处理器
register_exception_handlers(app)



app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)

app.include_router(history.router)