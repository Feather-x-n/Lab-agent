from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from common.exceptions import BusinessException
from utils.jwt import decode_access_token
from database import get_db
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
def get_current_user(token: str = Depends(oauth2_scheme),db:Session = Depends(get_db))->User:
    """jwt token鉴权合法性"""
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="登录已失效")
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的登录凭证"
        )
    user = db.query(User).filter(User.id == user_id).first()
    if user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户被禁用"
        )
    return user
# 鉴权认证管理员权限
def get_current_admin(current_user:User = Depends(get_current_user))->User:
    if current_user.role != "admin":
        raise BusinessException(message="无权限访问",code=403)
    return current_user