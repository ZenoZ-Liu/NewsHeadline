
from fastapi import APIRouter, Depends,HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession

from crud import users
from modules.users import User
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdateRequest, UserChangePasswordRequest
from config.db_conf import get_db
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/user", tags=["users"])

@router.post("/register")
async def register_user(user_data:UserRequest,db:AsyncSession = Depends(get_db)):
    # 注册逻辑：验证用户是否存在 -> 新增用户 -> 生成 Token -> 响应结果
    # 根据用户名查询数据库
    db_user = await users.get_user_by_username(db, user_data.username)
    if db_user:
        return{
            "code":400,
            "message":"用户已存在",
            "data":None

        }

    # 新增用户
    user = await users.create_user(db, user_data)

    # 生成 Token
    token = await users.create_token(db, user.id)

    # return {
    #     "code": 200,
    #     "message": "注册成功",
    #     "data": {
    #         "token": token,
    #         "userInfo": {
    #             "id": user.id,
    #             "username": user_data.username,
    #             "bio": user.bio,
    #             "avatar": user.avatar
    #         }
    #     }
    # }
    response_data = UserAuthResponse(token=token,userInfo=UserInfoResponse.model_validate(user))
    return success_response(data=response_data)

@router.post("/login")
async def login_user(user_data:UserRequest,db:AsyncSession = Depends(get_db)):
    user = await users.authenticate_user(db,user_data.username,user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="用户名或密码错误")
    token = await users.create_token(db, user.id)
    response_data = UserAuthResponse(token=token,user_info=UserInfoResponse.model_validate(user))
    return success_response(data=response_data)

@router.get("/info")
def get_user_info(user:User =Depends(get_current_user)):
    return success_response(
        message="获取用户信息成功",
        data=UserInfoResponse.model_validate(user)
    )

@router.put("/update")
async def update_user_info(
        user_data:UserUpdateRequest,
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    updated_user = await users.update_user(db,user.username,user_data)
    return success_response(
        message="更新用户信息成功",
        data=UserInfoResponse.model_validate(updated_user)
)

@router.put("/password")
async def update_password(
        password_data:UserChangePasswordRequest,
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_db)
):
    res_change_pwd = await users.change_password(
        db,
        user,
        password_data.old_password,
        password_data.new_password
    )
    if not res_change_pwd:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="修改密码失败，请检查旧密码")

    return success_response(message="修改密码成功")

