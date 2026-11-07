from sqlalchemy.orm import Session
from common.exceptions import BusinessException
from common.response import PageResponse
from models.equipemnt import Equipment
from schemas.equipment import EquipmentResponse, EquipmentCreateRequest, EquipmentUpdateRequest
from models.lab import Lab

def get_equipment_list(
        db:Session,
        page: int,
        page_size: int,
        keywords: str,
        lab_id:int
):
    query = db.query(Equipment)
    if lab_id:
        query = query.filter(Equipment.lab_id == lab_id)
    if keywords:
        query = query.filter(Equipment.name.contains(keywords))
    total = query.count()
    equipments = (query.offset((page-1) * page_size).limit(page_size).all())
    result = []
    for equipment in equipments:
        res = EquipmentResponse.model_validate(equipment)
        res.lab_name = equipment.lab.name if equipment.lab else None
        result.append(res)
    return PageResponse(list = result, total = total)
def create_equipment(
        db:Session,
        data:EquipmentCreateRequest,
):
    exist = db.query(Equipment).filter(Equipment.name == data.name).first()
    if exist:
        raise BusinessException(message="实验设备已存在")
    equipment = Equipment(**data.model_dump())
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    res = EquipmentResponse.model_validate(equipment)
    res.lab_name = equipment.lab.name if equipment.lab else None
    return res
def update_equipment(
        db:Session,
        equipment_id:int,
        data:EquipmentUpdateRequest
):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise BusinessException(message="该设备不存在")
    payload = data.model_dump(exclude_none=True)
    lab_id = payload.get("lab_id", equipment.lab_id)
    name = payload.get("name", equipment.name)
    lab = db.query(Lab).filter(Lab.id == lab_id).first()
    if not lab:
        raise BusinessException(message="实验室不存在")
    exist = (
        db.query(Equipment)
        .filter(
            Equipment.lab_id == lab_id,
            Equipment.name == name,
            Equipment.id != equipment.id,
        )
        .first()
    )
    if exist:
        raise BusinessException(message="同一个实验室不能存在同名的设备")
    for filed, value in payload.items():
        setattr(equipment, filed, value)
    db.commit()
    db.refresh(equipment)
    res = EquipmentResponse.model_validate(equipment)
    res.lab_name = equipment.lab.name if equipment.lab else None
    return EquipmentResponse.model_validate(equipment)
def delete_equipment(
        db:Session,
        equipment_id:int,
):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise BusinessException(message="该设备不存在")
    db.delete(equipment)
    db.commit()

