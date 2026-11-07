from sqlalchemy.orm import Session
from models.user import User
from langchain_core.tools import tool
from services import kb_service,lab_service,equipment_service,reservation_service
from models.reservation import Reservation
from common.exceptions import BusinessException
from datetime import datetime
from schemas.reservation import ReservationCreateRequest
import json
def build_tools(db:Session,current_user:User):
    @tool
    def search_lab_docs(query:str)->str:
        """
         根据用户的提问检索知识库
        """
        try:
            r = kb_service.similarity_search(query, top_k=3)
            docs = r.get("documents", [[]])[0]  # ② 取出文档文本
            if not docs:
                return json.dumps({"ok": False, "error": "知识库没有检索到相关内容"}, ensure_ascii=False)
            return "\n\n".join(docs)  # ③ 返回字符串，不是 chroma 的原始 dict
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False)
        # 定义工具

    @tool(parse_docstring=True)
    def list_open_labs(keywords: str = ""):
        """
        查询实验室的工具

        Args:
            keywords: 查询实验室所需的关键字
        """
        page = lab_service.get_lab_page_list(db, page=1, page_size=10, keywords=keywords, status=1)
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
    def list_lab_equipments(lab_id: int, keywords: str = ""):
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

    @tool
    def create_lab_reservation(
            lab_id: int,
            date: str,
            start_time: str,
            end_time: str,
            equipment_id: int | None = None,
            remark: str | None = None,
    ) -> str:
        """创建预约单预约实验室或设备"""
        try:
            # ④ 用 Pydantic 请求模型，别把 ORM 的 Reservation 当入参
            req = ReservationCreateRequest(
                lab_id=lab_id,
                equipment_id=equipment_id,
                date=date,
                start_time=start_time,
                end_time=end_time,
                remark=remark,
            )
            reservation_service.create_reservation(db, current_user, req)
            return json.dumps({"ok": True, "message": "预约已提交，等待管理员审核"}, ensure_ascii=False)
        except BusinessException as exc:
            return json.dumps({"ok": False, "error": exc.message}, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)

    @tool
    def get_today() -> str:
        """获取服务器当前的日期  2026-09-20"""
        now = datetime.now()
        return now.strftime("%Y-%m-%d")

    return [list_open_labs, list_lab_equipments,create_lab_reservation,get_today,search_lab_docs]