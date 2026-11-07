from sqlalchemy.orm import Session

from common.response import PageResponse
from utils.password import  verify_password,hash_password
from models.user import User
from schemas.user import UserResponse, UserUpdateRequest
from common.exceptions import BusinessException
from operator import or_
from schemas.user import UserCreateRequest
def get_user_info(user: User):
    return UserResponse.model_validate(user)
def update_user_info(db:Session, user: User, data:UserUpdateRequest):
    """用户更改自己的用户信息"""
    user_dict = data.model_dump(exclude_none=True,exclude={"role", "status", "password"})
    for field, value in user_dict.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)
def update_password(db:Session, user: User, data:UserUpdateRequest):
    """修改密码"""
    if not verify_password(data.old_password, user.password):
        raise BusinessException(message="原密码错误")
    if data.old_password == data.new_password:
        raise BusinessException(message="新密码不能与原密码相同")
    change_password = hash_password(data.new_password)
    user.password = change_password
    db.commit()
    db.refresh(user)
def get_user_page_list(
        db:Session,
        page:int,
        page_size:int,
        keywords:str):
    """模糊查询"""
    query = db.query(User)
    if keywords:
        query = query.filter(or_(User.username.ilike(f"%{keywords}%"), User.name.ilike(f"%{keywords}%")))
    total = query.count()
    items = (
        query.order_by(User.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PageResponse(list=[UserResponse.model_validate(item) for item in items], total=total)
def create_user(db:Session, data:UserCreateRequest):
    exit = db.query(User).filter(User.username == data.username).first()
    if exit:
        raise BusinessException(message="账号已存在")
    user = User(
        username=data.username,
        password=hash_password(data.password),
        name=data.name,
        email=data.email,
        role=data.role,
        status=data.status,
        avatar=data.avatar,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)
def update_user(db:Session, user_id: int, data:UserUpdateRequest):
    """更新用户消息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise BusinessException(message="用户不存在")
    payload = data.model_dump(exclude_none=True)
    for filed, value in payload.items():
        setattr(user, filed, value)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)
def delete_user(db:Session, user_id: int,current_user: User):
    if user_id == current_user.id:
        raise BusinessException(message="不支持删除当前登录用户")
    res = db.query(User).filter(User.id == user_id).first()
    if not res:
        raise BusinessException(message="该用户不存在")
    db.delete(res)
    db.commit()
