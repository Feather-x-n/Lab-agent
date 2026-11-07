import shutil
from pathlib import Path
import uuid
from fastapi import APIRouter, UploadFile,File
import os
from common.exceptions import BusinessException
from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE,UPLOAD_DIR
import time
from common.response import Response
file_router = APIRouter(prefix="/api/files", tags=["文件管理"])
@file_router.post("/upload")
def upload_file(file: UploadFile = File(...)):
    """文件上传接口"""
    if not file.filename:
        raise BusinessException(message="文件名不能为空")
    # 获取文件原始文件名
    original_filename = os.path.basename(file.filename)
    #获取文件后缀
    ext = Path(original_filename).suffix.lower()
    # 文件后缀校验
    if ext not in ALLOWED_EXTENSIONS:
        raise BusinessException(message=f"不支持{ext}后缀的文件")
    # 文件大小检验
    if file.size and file.size > MAX_FILE_SIZE:
        raise BusinessException(message=f"文件不能超过 {MAX_FILE_SIZE // 1024 // 1024}MB")
    # 设置唯一的文件名
    disk_name = f"{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}{ext}"
    # 文件存储的实际路径
    save_path = UPLOAD_DIR / disk_name
    # 流式写文件
    with open(save_path, mode="wb") as f:
        shutil.copyfileobj(file.file, f)

    return Response.success(
        data={
            "original_name": original_filename,
            "disk_name": disk_name,
            "size": file.size,
            "url": f"/uploads/{disk_name}",
        }
    )