from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from . import utils_wrappers
from .jobs import JobManager
from pydantic import BaseModel

router = APIRouter()


class StagePayload(BaseModel):
    discipline: str
    module: str
    concept: str
    tipo: str
    difficulty: Any
    statement: str
    author: str | None = None
    tags: list[str] | None = None


@router.post("/exercises/stage")
def stage_exercise(payload: StagePayload):
    try:
        meta = utils_wrappers.make_staged(payload.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "staged", "meta": meta}


@router.get("/staging/{staged_id}/preview")
def get_staging_preview(staged_id: str):
    try:
        preview = utils_wrappers.get_staging_preview(staged_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="staged_id not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"staged_id": staged_id, "preview": preview}


class ConfirmPayload(BaseModel):
    action: str


@router.post("/staging/{staged_id}/confirm")
def confirm_staging(staged_id: str, payload: ConfirmPayload):
    if payload.action not in ("promote", "discard"):
        raise HTTPException(status_code=400, detail="invalid action")
    try:
        result = utils_wrappers.confirm_staged(staged_id, payload.action)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="staged_id not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"staged_id": staged_id, "result": result}


class SebentaGeneratePayload(BaseModel):
    discipline: str | None = None
    module: str | None = None
    concept: str | None = None
    tipo: str | None = None
    no_preview: bool | None = True
    no_compile: bool | None = True
    auto_approve: bool | None = True


@router.post("/sebentas/generate")
def generate_sebenta(payload: SebentaGeneratePayload):
    jm = JobManager()
    job_payload = payload.model_dump(exclude_none=True)
    job_id = jm.submit_job("sebenta_generate", job_payload)
    return {"job_id": job_id}


@router.get("/sebentas/status/{job_id}")
def sebenta_status(job_id: str):
    jm = JobManager()
    status = jm.get_job_status(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail="job not found")
    return status
