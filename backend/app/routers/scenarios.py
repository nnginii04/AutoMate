from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    RunAllScenariosResponse,
    TestScenario,
    TestScenarioRunRequest,
    TestScenarioRunResponse,
)
from app.services import ScenarioService

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.get("", response_model=list[TestScenario])
def list_scenarios(db: Session = Depends(get_db)) -> list[TestScenario]:
    return ScenarioService(db).list_scenarios()


@router.post("/run-all", response_model=RunAllScenariosResponse)
def run_all_scenarios(db: Session = Depends(get_db)) -> RunAllScenariosResponse:
    return ScenarioService(db).run_all()


@router.post("/run/{scenario_id}", response_model=TestScenarioRunResponse)
def run_scenario_by_path(
    scenario_id: str,
    request: Optional[TestScenarioRunRequest] = None,
    db: Session = Depends(get_db),
) -> TestScenarioRunResponse:
    result = ScenarioService(db).run_scenario(scenario_id, request)
    if not result:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
    return result


@router.get("/{scenario_id}", response_model=TestScenario)
def get_scenario(scenario_id: str, db: Session = Depends(get_db)) -> TestScenario:
    scenario = ScenarioService(db).get_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
    return scenario


@router.post("/{scenario_id}/run", response_model=TestScenarioRunResponse)
def run_scenario_legacy(
    scenario_id: str,
    request: Optional[TestScenarioRunRequest] = None,
    db: Session = Depends(get_db),
) -> TestScenarioRunResponse:
    result = ScenarioService(db).run_scenario(scenario_id, request)
    if not result:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
    return result
