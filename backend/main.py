from fastapi import FastAPI,HTTPException
from fastapi.staticfiles import StaticFiles
from api.file import file_router
from models.user import User
from models.lab import Lab
from models.equipemnt import Equipment
from models.reservation import Reservation
from fastapi.exceptions import RequestValidationError
from database import Base, engine
from api.auth import auth_router
from api.user import user_router
from api.lab import lab_router
from api.equipment import equ_router
from api.reservation import reservation_router
from api.ai import ai_router
from common.exceptions import (
    BusinessException,
    bussiness_exception_hadler,
    http_excpetion_hadler,
    validation_excpetion_hadler,
    global_excpetion_hadler
)
from starlette.middleware.cors import CORSMiddleware
from config import UPLOAD_DIR
import asyncio
from services import reservation_service
from contextlib import asynccontextmanager
#sqlachemy的orm映射可以直接创建数据库中不存在的表
Base.metadata.create_all(bind=engine)
@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(
        reservation_service.run_expire_scan()
    )  # 启动项目开启异步的扫描任务
    yield
    task.cancel()  # 关闭项目同时取消异步任务
app = FastAPI(lifespan=lifespan)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174"
]
app.add_middleware(CORSMiddleware, allow_origins=origins,allow_credentials = True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth_router)
app.include_router(file_router)
app.include_router(user_router)
app.include_router(lab_router)
app.include_router(equ_router)
app.include_router(reservation_router)
app.include_router(ai_router)
# 挂载静态资源：/uploads/xxx.jpg → uploads/xxx.jpg
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.add_exception_handler(BusinessException, bussiness_exception_hadler)
app.add_exception_handler(HTTPException, http_excpetion_hadler)
app.add_exception_handler(RequestValidationError, validation_excpetion_hadler)
app.add_exception_handler(Exception, global_excpetion_hadler)
@app.get("/")
def root():
    return {"msg":"ok"}
