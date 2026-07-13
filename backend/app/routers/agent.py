from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AgentRunRequest, AgentRunResponse
from app.services import AgentService

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/run", response_model=AgentRunResponse)
def run_agent(
    request: AgentRunRequest,
    db: Session = Depends(get_db),
    x_session_id: Optional[str] = Header(default=None),
) -> AgentRunResponse:
    service = AgentService(db)
    return service.run(request, session_id=x_session_id)
