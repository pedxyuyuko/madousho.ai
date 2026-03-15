"""Flow CRUD API endpoints - 流程增删查改接口"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.madousho.models.flow import Flow
from madousho.api.deps import get_db
from madousho.api.errors import error_response
from madousho.api.schemas.flow import FlowCreate, FlowResponse, FlowListResponse

router = APIRouter()


@router.get("", response_model=FlowListResponse)
def list_flows(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    plugin: str | None = Query(None),
    name: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """列出所有流程，支持分页和筛选。

    Args:
        offset: 分页偏移量
        limit: 每页数量 (1-100)
        status: 按状态筛选
        plugin: 按插件筛选
        name: 按名称搜索 (模糊匹配)
        db: 数据库会话

    Returns:
        FlowListResponse: 分页的流程列表
    """
    query = db.query(Flow)

    # 应用筛选条件
    if status is not None:
        query = query.filter(Flow.status == status)
    if plugin is not None:
        query = query.filter(Flow.plugin == plugin)
    if name is not None:
        query = query.filter(Flow.name.ilike(f"%{name}%"))

    # 获取总数
    total = query.count()

    # 按 created_at 降序排列并分页
    items = query.order_by(Flow.created_at.desc()).offset(offset).limit(limit).all()

    # 转换为响应模型
    flow_items = [
        FlowResponse(
            uuid=flow.uuid,
            name=flow.name,
            description=flow.description,
            plugin=flow.plugin,
            tasks=flow.tasks,
            status=flow.status,
            flow_template=flow.flow_template,
            created_at=flow.created_at,
        )
        for flow in items
    ]

    return FlowListResponse(
        items=flow_items,
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{uuid}", response_model=FlowResponse)
def get_flow(
    uuid: str,
    db: Session = Depends(get_db),
):
    """获取单个流程详情。

    Args:
        uuid: 流程唯一标识符
        db: 数据库会话

    Returns:
        FlowResponse: 流程详情

    Raises:
        HTTPException: 404 流程不存在
    """
    flow = db.query(Flow).filter(Flow.uuid == uuid).first()

    if flow is None:
        return error_response(404, "flow_not_found", f"Flow {uuid} not found")

    return FlowResponse(
        uuid=flow.uuid,
        name=flow.name,
        description=flow.description,
        plugin=flow.plugin,
        tasks=flow.tasks,
        status=flow.status,
        flow_template=flow.flow_template,
        created_at=flow.created_at,
    )


@router.post("", status_code=201)
def create_flow(
    flow: FlowCreate,
    db: Session = Depends(get_db),
):
    """创建新流程。

    Args:
        flow: 流程创建请求体
        db: 数据库会话

    Returns:
        dict: 包含新流程 UUID 的响应
    """
    new_uuid = str(uuid.uuid4())

    new_flow = Flow(
        uuid=new_uuid,
        name=flow.name,
        plugin=flow.plugin,
        flow_template=flow.flow_template,
        description=flow.description,
        status="created",
        created_at=datetime.now(timezone.utc),
    )

    db.add(new_flow)
    db.commit()

    return {"uuid": new_uuid}
