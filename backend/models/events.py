"""Pydantic models for SSE events and investigation data."""

from typing import Optional

from pydantic import BaseModel

from models.enums import ClassificationCategory, SignalSeverity, StepStatus


class InvestigateRequest(BaseModel):
    url: str


class Signal(BaseModel):
    name: str
    severity: SignalSeverity
    segmentsFilled: int


class InvestigationEvent(BaseModel):
    step: str
    status: StepStatus
    data: Optional[dict] = None


class VerdictResult(BaseModel):
    category: ClassificationCategory
    confidence: float
    reasoning: str
    signals: list[Signal]
