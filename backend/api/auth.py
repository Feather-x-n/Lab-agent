from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas.auth import LoginRequest, LoginResponse, RegisterRequest
from models.user import User
from schemas.user import UserResponse
from utils.password import verify_password
from utils.jwt import create_access_token
from common.response import Response
from common.exceptions import BusinessException
from services import auth_service
auth_router = APIRouter(prefix="/api/auth", tags=["权限验证"])
@auth_router.post("/login")
def login(data: LoginRequest,db:Session = Depends(get_db)):
    result = auth_service.login(db,data)
    return Response.success(
        message="登录成功",
        data=result,
    )
@auth_router.post("/register")
def register(data: RegisterRequest,db:Session = Depends(get_db)):
    auth_service.register(db,data)
    return Response.success(message="注册成功")