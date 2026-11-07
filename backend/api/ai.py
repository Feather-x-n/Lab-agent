import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from common.response import Response
from common.exceptions import BusinessException
from database import get_db
from dependencies.auth import get_current_user
from models.user import User
from schemas.ai import ChatMessage, ChatRequest
from services import ai_service
from services import agent_service
ai_router = APIRouter(prefix="/api/ai", tags=["AI相关的API"])
@ai_router.post("/chat")
def chat(data: ChatRequest, current_user: User = Depends(get_current_user),db:Session = Depends(get_db)):
    content = agent_service.run_agent(db, current_user, data)
    return Response.success(data=ChatMessage(role="assistant", content=content))

@ai_router.post("/chat/stream")
def chat_stream(data: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 参数错误要在开始流式输出前抛，才能走统一的 JSON 异常处理
    if not data.messages:
        raise BusinessException(message="对话内容为空")
    return StreamingResponse(
        agent_service.run_agent_stream(db, current_user, data),
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

@ai_router.post("/chat/events")
def chat_events(data: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """事件流（NDJSON）：逐行输出 token / tool_call / tool_result / node，供前端展示工作流程"""
    if not data.messages:
        raise BusinessException(message="对话内容为空")

    def gen():
        for event in agent_service.run_agent_events(db, current_user, data):
            yield json.dumps(event, ensure_ascii=False) + "\n"

    return StreamingResponse(
        gen(),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )