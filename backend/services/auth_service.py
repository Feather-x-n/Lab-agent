from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas.auth import LoginRequest, LoginResponse, RegisterRequest
from models.user import User
from schemas.user import UserResponse
from utils.password import verify_password, hash_password
from utils.jwt import create_access_token
from common.response import Response
from common.exceptions import BusinessException
#登录服务
def login(db:Session,data:LoginRequest):
    res = db.query(User).filter(User.username == data.username).first()
    if not res:
        raise BusinessException(message="账号不存在")
    if not verify_password(data.password, res.password):
        raise BusinessException(message="密码错误")
    if res.status != 1:
        raise BusinessException(message="账号被禁用")
    token = create_access_token(res.id)
    return LoginResponse(token = token,user=UserResponse.model_validate(res))
#注册服务
def register(db:Session,data:RegisterRequest):
    res = db.query(User).filter(User.username == data.username).first()
    if res:
        raise BusinessException(message="用户名已存在")
    user = User(
        username = data.username,
        password=hash_password(data.password),
        name=data.name or data.username,
        role = "student",
        status = 1,
    )
    db.add(user)
    db.commit()
    db.refresh(user)