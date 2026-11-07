from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from common.response import Response
from schemas.lab import LabCreateRequest, LabUpdateRequest
from services import lab_service
from models.user import User
from database import get_db
from dependencies.auth import get_current_admin,get_current_user

lab_router = APIRouter(prefix="/api/lab", tags=["lab"])
@lab_router.get("/list")
def get_lab_list(
        page: int =1,
        page_size: int = 10,
        keywords: str | None = None,
        curreny_user:User = Depends(get_current_user),
        status: int | None = None,
        db:Session = Depends(get_db)
):
    res = lab_service.get_lab_page_list(db, page, page_size, keywords,status)
    return Response.success(data=res)
@lab_router.post("")
def create_lab(
        data:LabCreateRequest,
        current_user:User = Depends(get_current_admin),
        db:Session = Depends(get_db),
):
    res = lab_service.creat_lab(db, data)
    return Response.success(data=res)
@lab_router.put("/{lab_id}")
def update_labInfo(
        lab_id: int,
        data: LabUpdateRequest,
        current_user:User = Depends(get_current_admin),
        db:Session = Depends(get_db),
):
    res = lab_service.update_lab(db, lab_id, data)
    return Response.success(data=res)
@lab_router.get("/{lab_id}")
def get_lab(
    lab_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    res = lab_service.get_lab(db, lab_id)
    return Response.success(data=res)
@lab_router.delete("/{lab_id}")
def delete_lab(
        lab_id: int,
        current_user:User = Depends(get_current_admin),
        db:Session = Depends(get_db),
):
    lab_service.delete_lab(db, lab_id)
    return Response.success(message="操作成功")
