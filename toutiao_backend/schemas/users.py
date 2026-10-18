from typing import Optional

from pydantic import BaseModel, ConfigDict,Field


class UserRequest(BaseModel):
    username: str
    password: str


class UserInfoBase(BaseModel):
    nickname:Optional[str] = Field(None,max_length = 50,description = "昵称")
    avatar:Optional[str] = Field(None,max_length = 255,description = "头像URL")
    gender:Optional[str] = Field(None,max_length = 10,description = "性别")
    bio:Optional[str] = Field(None,max_length = 500,description = "个人简介")


class UserInfoResponse(UserInfoBase):
    id: int
    username: str

    # 模型类配置
    model_config = ConfigDict(
        from_attributes=True    # 从对象属性读值，用于 ORM 模型对象转响应模型
    )

class UserAuthResponse(BaseModel):
    token:str
    user_info:UserInfoResponse = Field(...,alias="userInfo")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True # alias / 字段名兼容
    )

class UserUpdateRequest(BaseModel):
    nickname: str = None
    avatar: str = None
    gender: str = None
    bio: str = None
    phone: str = None

class UserChangePasswordRequest(BaseModel):
    old_password: str = Field(..., alias="oldPassword", description="旧密码")
    new_password: str = Field(..., min_length=6, alias="newPassword", description="新密码")