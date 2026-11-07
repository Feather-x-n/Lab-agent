from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import current_user
from common.exceptions import BusinessException
from common.response import Response
from schemas.auth import UpdatePasswordRequest
from services import user_service
from database import get_db
from schemas.user import UserResponse, UserCreateRequest
from dependencies.auth import get_current_user
from models.user import User
from schemas.user import UserUpdateRequest
from dependencies.auth import get_current_admin
user_router = APIRouter(prefix="/api/user", tags=["用户信息接口"])
@user_router.get("/me")
def get_user_info(current_user:User = Depends(get_current_user)):
    return {
        "code": 200,
        "message": "请求成功",
        "data": UserResponse.model_validate(current_user),
    }
@user_router.put("/me")
def update_user(data:UserUpdateRequest,
                current_user:User = Depends(get_current_user),
                db:Session = Depends(get_db)
                ):
    """更新当前用户信息"""
    res = user_service.update_user_info(db,current_user,data)
    if not res:
        raise BusinessException(message="更新失败")
    return Response.success(data=res)
@user_router.put("/password")
def update_password(
        data:UpdatePasswordRequest,
        current_user:User = Depends(get_current_user),
        db:Session = Depends(get_db)
):
    user_service.update_password(db,current_user,data)
    return Response.success(message="密码修改成功")
@user_router.get("/list")
def get_user_list(
        page:int = 1,
        page_size:int = 10,
        keywords:str|None = None,
        current_user:User = Depends(get_current_admin),
        db:Session = Depends(get_db)
):
    res = user_service.get_user_page_list(db,page,page_size,keywords)
    return Response.success(data=res)
@user_router.post("")
def create_user(data:UserCreateRequest,current_user:User = Depends(get_current_admin),db:Session = Depends(get_db)):
    res = user_service.create_user(db,data)
    if not res:
        raise BusinessException(message="业务出现异常")
    return Response.success(data=res)
@user_router.put("/{user_id}")
def update_user(
    user_id: int,
    data:UserUpdateRequest,
    current_user:User = Depends(get_current_admin),
    db:Session = Depends(get_db),
):
    res = user_service.update_user(db,user_id,data)
    return Response.success(data=res)
@user_router.delete("/{user_id}")
def delete_user(
        user_id:int,
        current_user:User = Depends(get_current_admin),
        db:Session = Depends(get_db)
):
    res = user_service.delete_user(db, user_id, current_user)
    return Response.success()


