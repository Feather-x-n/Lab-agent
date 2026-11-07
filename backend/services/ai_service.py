from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.embeddings import init_embeddings
from rich import print as rprint
from sqlalchemy.orm import Session
from fastapi import Depends
from database import get_db
from services import kb_service
from common.exceptions import BusinessException
from schemas.ai import ChatRequest
from langchain_core.tools import tool
from services import lab_service
from services import equipment_service
import json
SYSTEM_PROMPT = """你是智能实验室预约系统的助手，回答要简洁。
你可以介绍本系统的预约流程：
1. 登录后打开实验室列表，选择实验室或设备
2. 填写日期和时段并提交，状态为待审核
3. 管理员审核通过后即可使用
4. 待审核、已通过的预约，本人可以取消
涉及实验室、设备的问题，你必须先调用工具查询真实数据，再根据工具结果回答：
- list_open_labs：按关键字查询正在开放的实验室（名称、位置、容量、开放时间）
- list_lab_equipments：查询某个实验室里的设备（需要实验室 id）

回答规则：
1. 查到了就据实回答，不要编造工具里没有的数据。
2. 工具返回空或查不到，就如实说没查到，并建议用户去【实验室列表】页查看。
3. 预约流程：登录 → 实验室列表 → 选实验室/设备 → 填日期和时段 → 提交（待审核）→ 管理员审核通过后可用；待审核和已通过的预约本人可取消。
以下是实验室相关的规章制度资料，回答这类问题时请优先依据它：
{context}
如果用户问了跟实验室无关的问题，可以直接拒绝回答。
"""
def init_model():
    LLM_MODEL = init_chat_model(
        model="qwen2.5:7b",
        model_provider="ollama"
    )
    return LLM_MODEL
llm = init_model()
def build_tools(db:Session):
    # 定义工具
    @tool(parse_docstring=True)
    def list_open_labs(keywords: str =""):
        """
        查询实验室的工具

        Args:
            keywords: 查询实验室所需的关键字
        """
        page = lab_service.get_lab_page_list(db, page =1,page_size=10, keywords=keywords, status=1)
        rows = [
            {
                "id": item.id,
                "name": item.name,
                "location": item.location,
                "capacity": item.capacity,
                "open_time": item.open_time,
                "close_time": item.close_time,
            }
            for item in page.list
        ]
        return json.dumps({"total": page.total, "rows": rows}, ensure_ascii=False)

    @tool(parse_docstring=True)
    def list_lab_equipments(lab_id: int, keywords: str =""):
        """
        查询实验室设备的工具

        Args:
             lab_id: 查询目标实验室的id
             keywords: 查询实验室设备的关键字
        """
        if not lab_id:
            return json.dumps({"error": "缺少实验室 id"}, ensure_ascii=False)
        page = equipment_service.get_equipment_list(db, page=1, page_size=10, lab_id=int(lab_id), keywords=keywords)
        rows = [
            {
                "id": item.id,
                "name": item.name,
                "lab_id": item.lab_id,
                "lab_name": item.lab_name,
                "spec": item.spec,
                "quantity": item.quantity,
                "status": item.status,
            }
            for item in page.list
        ]
        return json.dumps({"total": page.total, "rows": rows}, ensure_ascii=False)

    return [list_open_labs, list_lab_equipments]

def chat(data:ChatRequest,db:Session):
    if not data.messages:
        raise BusinessException(message="对话内容为空")
    history = []
    user_query = ""
    for message in data.messages:
        if message.role in ("user", "assistant") and message.content.strip():
            history.append(message.model_dump())
            if message.role == "user":
                user_query = message.content.strip()
    if not history:
        raise BusinessException(message="请输入您要对话的内容")
        # ========== 新增：RAG向量检索 ==========
    context_text = ""
    if user_query:
        try:
            search_result = kb_service.similarity_search(user_query, top_k=3)
            docs = search_result.get("documents", [[]])[0]
            if docs:
                context_text = "\n".join(docs)
        except Exception as e:
            rprint(f"[RAG] 检索失败，降级为无资料回答: {e}")
            context_text = ""
    agent = create_agent(
        model=llm,
        tools=build_tools(db),
        system_prompt=SYSTEM_PROMPT.format(context=context_text or "（本次没有检索到资料）"),
    )
    result = agent.invoke({"messages": history})
    last = result["messages"][-1]
    content = last.content if isinstance(last.content, str) else str(last.content)
    if not content or not content.strip():
        raise BusinessException(message="大模型没有返回内容")
    return content


