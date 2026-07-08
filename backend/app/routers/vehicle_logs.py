from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ExecutionLogResponse, VehicleState
from app.services import LogService
from app.services.vehicle_service import vehicle_state_store

router = APIRouter(tags=["vehicle", "logs"])


@router.get("/vehicle/state", response_model=VehicleState)
def get_vehicle_state() -> VehicleState:
    return vehicle_state_store.get()


@router.patch("/vehicle/state", response_model=VehicleState)
def update_vehicle_state(partial: dict) -> VehicleState:
    return vehicle_state_store.update(partial)


@router.get("/logs", response_model=list[ExecutionLogResponse])
def list_logs(db: Session = Depends(get_db)) -> list[ExecutionLogResponse]:
    return LogService(db).list_logs()


@router.get("/logs/{log_id}", response_model=ExecutionLogResponse)
def get_log(log_id: int, db: Session = Depends(get_db)) -> ExecutionLogResponse:
    log = LogService(db).get_log(log_id)
    if not log:
        raise HTTPException(status_code=404, detail=f"Log {log_id} not found")
    return log
