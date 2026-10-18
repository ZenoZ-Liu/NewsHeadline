from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update
from modules.users import User,UserToken
from schemas.users import UserRequest, UserUpdateRequest
from utils import security
import uuid
from datetime import datetime, timedelta


async def get_user_by_username(db:AsyncSession,username:str):
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_user(db:AsyncSession,user_data:UserRequest):
    hashed_password = security.get_has_password(user_data.password)
    user =User(username = user_data.username,password = hashed_password)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_token(db:AsyncSession,user_id:int):
    # 生成 Token
    token = str(uuid.uuid4())

    # 设置过期时间
    expire_date = datetime.now() + timedelta(days=7)

    # 查询当前用户是否有 token
    query = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(query)
    user_token =result.scalar_one_or_none()

    if user_token:
        user_token.token =token
        user_token.expires_at = expire_date
        await db.commit()
    else:
        user_token = UserToken(user_id = user_id, token = token,expires_at= expire_date)
        db.add(user_token)
        await db.commit()
        await db.refresh(user_token)

    return token


# 用户验证
async def authenticate_user(db:AsyncSession,username:str, password:str):
    user = await get_user_by_username(db,username)
    if not user:
        return None

    if not security.verify_password(password,user.password):
        return None

    return user

# 根据 Token 查询用户
async def get_user_by_token(db:AsyncSession,token:str):
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    db_token = result.scalar_one_or_none()

    # Token 不存在或已过期
    if not db_token or db_token.expires_at < datetime.now():
        return None

    # 查询用户信息
    query_user = select(User).where(User.id == db_token.user_id)
    result_user = await db.execute(query_user)
    user = result_user.scalar_one_or_none()

    return user


async def update_user(
        db: AsyncSession,
        username: str,
        user_data: UserUpdateRequest
):
    # 查询用户
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return None

    # 更新用户信息
    # **user_data表示将user_data对象的属性展开为关键字参数传递给update函数
    # model.dump() 将 Pydantic 模型对象转换为字典,
    # exclude_unset=True 只包含已设置的字段,exclude_none=True 排除值为 None 的字段
    update_stmt = (
        update(User)
        .where(User.username == username)
        .values(**user_data.model_dump(
            exclude_unset=True,
            exclude_none=True
        )
                )
    )
    result = await db.execute(update_stmt)
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="用户不存在")
    # 查询更新后的用户信息
    updated_user = await get_user_by_username(db,username)
    return updated_user



async def change_password(
        db:AsyncSession,
        user:User,
        old_password:str,
        new_password:str
):
    if not security.verify_password(old_password, user.password):
        return False
    hashed_new_password = security.get_has_password(new_password)
    user.password = hashed_new_password

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return True
