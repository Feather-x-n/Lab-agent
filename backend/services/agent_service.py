from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage
from langgraph.graph import MessagesState, StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from sqlalchemy.orm import Session
from models.user import User
from schemas.ai import ChatRequest
from services import agent_tools
from common.exceptions import BusinessException

SYSTEM_PROMPT = """你是智能实验室预约系统的 Agent，回答要简洁。
你可以：
1. 使用 search_lab_docs 查询实验室的规则、安全、开放时间等问题
2. 使用 list_open_labs / list_lab_equipments 查询真实的实验室和设备
3. 在用户确认预约后，使用 create_lab_reservation 进行真实的预约落库
4. 使用 get_today 来进行日期的换算
## 必须遵守
当用户提到 今天、明天、后天 等日期时，先调用 get_today，不要直接说无法确定。
提交预约前必须复述：实验室ID与名称（或设备ID和名称）、日期、开始时间、结束时间，并得到用户确认。
用户没说【确认】【确认预约】【就这样预约】之前，不要调用 create_lab_reservation。
缺少 lab_id 时先调 list_open_labs；缺少 equipment_id 时先调 list_lab_equipments。
预约成功后状态是待审核，需要管理员审核通过后才能使用。
不要编造数据库里没有的实验室或设备信息。
问开放时间或实验室规则时，优先调用 search_lab_docs。

今天是 {today}（服务器时间）。用户说"明天"就是今天的下一天，不需要调用 get_today 自己推算。

## 预约规则
1. 用户表达预约意图时，复述一次【实验室名称+ID、日期、开始时间、结束时间】，然后问"确认吗"。
2. 用户回复【确认】【确认预约】【可以】【就这样】【是的】等任意肯定词时，
   **必须立即调用 create_lab_reservation**，禁止再反问、禁止再次复述、禁止说"请继续"。
3. 复述信息只做一次，不要反复确认。
"""
import json, re, uuid
from langchain_core.messages import SystemMessage, AIMessage, AIMessageChunk, ToolMessage


def _repair_leaked_tool_call(msg: AIMessage, valid_names: set) -> AIMessage:
    """模型偶尔把 tool_call 当正文输出，这里把它还原成真正的 tool_calls"""
    if getattr(msg, "tool_calls", None):          # 已经是结构化的，不动
        return msg
    text = msg.content or ""
    if not isinstance(text, str) or '"arguments"' not in text:
        return msg
    m = re.search(
        r'\{\s*"name"\s*:\s*"([a-z_][a-z0-9_]*)"\s*,\s*"arguments"\s*:\s*(\{.*?\})\s*\}',
        text, re.S,
    )
    if not m:
        return msg
    name, raw_args = m.group(1), m.group(2)
    if name not in valid_names:                   # ★ 必须是已注册的工具，防止误伤普通文本
        return msg
    try:
        args = json.loads(raw_args)
    except Exception:
        return msg
    return AIMessage(
        content="",
        tool_calls=[{"name": name, "args": args,
                     "id": "call_" + uuid.uuid4().hex[:8], "type": "tool_call"}],
    )

def build_agent(db: Session, current_user: User):
    tools = agent_tools.build_tools(db, current_user)

    # ★ 关键：这里拿到的是"模型 + 工具定义"，不是 agent
    model = init_chat_model(
        model="qwen2.5:7b",
        model_provider="ollama",
    ).bind_tools(tools)
    valid_names = {t.name for t in tools}
    # ★ 节点里调模型，返回 {"messages": [消息]} —— 不是 list，也不是整份 state
    def agent_node(state: MessagesState):
        response = model.invoke([SystemMessage(content=SYSTEM_PROMPT), *state["messages"]])
        response = _repair_leaked_tool_call(response, valid_names)  # ★ 兜底修复
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent_node)          # LLM 节点
    graph.add_node("tools", ToolNode(tools))     # 工具执行节点
    graph.add_edge(START, "agent")               # 起点
    graph.add_conditional_edges("agent", tools_condition)   # 有 tool_calls → tools，否则 END
    graph.add_edge("tools", "agent")             # 工具结果回给模型
    return graph.compile()


def run_agent(db: Session, current_user: User, data: ChatRequest):
    if not data.messages:
        raise BusinessException(message="对话内容为空")

    history = []
    for message in data.messages:
        if message.role in ("user", "assistant") and message.content.strip():
            history.append(message.model_dump())

    if not history:
        raise BusinessException(message="请输入您要对话的内容")

    agent = build_agent(db, current_user)
    try:
        result = agent.invoke(
            {"messages": history},
            config={"recursion_limit": 25},      # 预约流程要多次工具往返，10 太小
        )
    except BusinessException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()                    # ★ 别把真实错误吞成"请稍后重试"
        raise BusinessException(message=f"大模型调用失败：{e}")

    last = result["messages"][-1]
    content = last.content if isinstance(last.content, str) else str(last.content)
    if not content or not content.strip():
        raise BusinessException(message="大模型没有返回内容")
    return content


def run_agent_stream(db: Session, current_user: User, data: ChatRequest):
    """流式版本：边生成边 yield 文本片段（工具调用阶段不输出内容）"""
    if not data.messages:
        raise BusinessException(message="对话内容为空")

    history = []
    for message in data.messages:
        if message.role in ("user", "assistant") and message.content.strip():
            history.append(message.model_dump())

    if not history:
        raise BusinessException(message="请输入您要对话的内容")

    agent = build_agent(db, current_user)
    try:
        for chunk, _meta in agent.stream(
            {"messages": history},
            config={"recursion_limit": 25},
            stream_mode="messages",
        ):
            if isinstance(chunk, AIMessageChunk):
                text = chunk.content
                if isinstance(text, str) and text:
                    yield text
    except BusinessException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise BusinessException(message=f"大模型调用失败：{e}")


def run_agent_events(db: Session, current_user: User, data: ChatRequest):
    """事件流版本：yield 结构化事件 dict
    {"type":"token","content":...}          模型输出的文本片段
    {"type":"tool_call","name":..,"args":..} 准备调用某个工具
    {"type":"tool_result","name":..,"ok":..,"preview":..} 工具返回
    {"type":"node","name":"agent"/"tools"}  图节点执行
    """
    if not data.messages:
        raise BusinessException(message="对话内容为空")

    history = []
    for message in data.messages:
        if message.role in ("user", "assistant") and message.content.strip():
            history.append(message.model_dump())

    if not history:
        raise BusinessException(message="请输入您要对话的内容")

    agent = build_agent(db, current_user)
    try:
        for mode, payload in agent.stream(
            {"messages": history},
            config={"recursion_limit": 25},
            stream_mode=["messages", "updates"],
        ):
            if mode == "messages":
                chunk, _meta = payload
                if isinstance(chunk, AIMessageChunk):
                    text = chunk.content
                    if isinstance(text, str) and text:
                        yield {"type": "token", "content": text}

            elif mode == "updates":
                for node_name, update in (payload or {}).items():
                    if not isinstance(update, dict):
                        continue
                    for m in update.get("messages") or []:
                        if isinstance(m, AIMessage) and getattr(m, "tool_calls", None):
                            for tc in m.tool_calls:
                                yield {
                                    "type": "tool_call",
                                    "name": tc.get("name"),
                                    "args": tc.get("args"),
                                }
                        elif isinstance(m, ToolMessage):
                            raw = m.content if isinstance(m.content, str) else str(m.content)
                            ok = not ('"ok": false' in raw or '"error"' in raw)
                            yield {
                                "type": "tool_result",
                                "name": getattr(m, "name", "") or node_name,
                                "ok": ok,
                                "preview": raw[:300],
                            }
                    yield {"type": "node", "name": node_name}
    except BusinessException as exc:
        yield {"type": "error", "message": exc.message}
    except Exception as e:
        import traceback
        traceback.print_exc()
        yield {"type": "error", "message": f"大模型调用失败：{e}"}
