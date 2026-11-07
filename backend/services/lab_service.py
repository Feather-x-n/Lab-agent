from sqlalchemy.orm import Session
from sqlalchemy import or_
from common.exceptions import BusinessException
from common.response import PageResponse
from models.lab import Lab
from schemas.lab import LabResponse, LabUpdateRequest
from  schemas.lab import LabCreateRequest


def get_lab_page_list(
        db:Session,
        page:int,
        page_size:int,
        keywords:str|None = None,
        status:int|None = None,
        ):
    query =db.query(Lab)
    if keywords:
        query = query.filter(
            or_(Lab.name.ilike(f"%{keywords}%"), Lab.location.ilike(f"%{keywords}%"))
        )
    if status:
        query = query.filter(Lab.status == status)
    total = query.count()
    items = (
        query.offset((page-1)*page_size).limit(page_size).all()
    )
    return PageResponse(
        list = [LabResponse.model_validate(item) for item in items],
        total = total,
    )
def creat_lab(db:Session,data:LabCreateRequest):
    exists = db.query(Lab).filter(Lab.name == data.name).first()
    if exists:
        raise BusinessException(message="该实验室已存在")
    lab = Lab(**data.model_dump())
    db.add(lab)
    db.commit()
    db.refresh(lab)
    return LabResponse.model_validate(lab)
def update_lab(db:Session,lab_id:int,data:LabUpdateRequest):
    lab = db.query(Lab).filter(Lab.id == lab_id).first()
    if not lab:
        raise BusinessException(message="实验室不存在")
    payload = data.model_dump(exclude_none=True)
    if "name" in payload:
        exists = (
            db.query(Lab)
            .filter(Lab.name == payload["name"], Lab.id != lab_id)
            .first()
        )
        if exists:
            raise BusinessException(message="实验室名称已存在")
    for field, value in payload.items():
        setattr(lab, field, value)
    db.commit()
    db.refresh(lab)
    return LabResponse.model_validate(lab)
def delete_lab(db: Session, lab_id: int):
    lab = db.query(Lab).filter(Lab.id == lab_id).first()
    if not lab:
        raise BusinessException(message="实验室不存在")
    db.delete(lab)
    db.commit()
def get_lab(db:Session, lab_id:int):
    lab = db.query(Lab).filter(Lab.id == lab_id).first()
    if not lab:
        raise BusinessException(message="没有此实验室")
    return LabResponse.model_validate(lab)