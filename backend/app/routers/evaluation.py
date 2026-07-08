from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import DistributionItem, EvaluationSummary
from app.services import EvaluationService

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.get("/summary", response_model=EvaluationSummary)
def get_evaluation_summary(db: Session = Depends(get_db)) -> EvaluationSummary:
    return EvaluationService(db).get_summary()


@router.get("/intent-distribution", response_model=list[DistributionItem])
def get_intent_distribution(db: Session = Depends(get_db)) -> list[DistributionItem]:
    return EvaluationService(db).get_intent_distribution()


@router.get("/tool-usage", response_model=list[DistributionItem])
def get_tool_usage(db: Session = Depends(get_db)) -> list[DistributionItem]:
    return EvaluationService(db).get_tool_usage()
