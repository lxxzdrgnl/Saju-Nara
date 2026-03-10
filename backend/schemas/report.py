"""요청/응답 Pydantic 스키마."""

from __future__ import annotations
from uuid import UUID
from pydantic import BaseModel


# ─── 요청 ───────────────────────────────────────────────────────────────────

class BirthRequest(BaseModel):
    birth_date: str       # "YYYY-MM-DD"
    birth_time: str       # "HH:MM"
    gender: str           # "male" | "female"
    calendar: str = "solar"
    is_leap_month: bool = False

class SajuRequest(BirthRequest):
    concern: str | None = None

class CompatibilityRequest(BaseModel):
    person1: BirthRequest
    person2: BirthRequest

class DailyRequest(BirthRequest):
    pass

class QuestionRequest(BirthRequest):
    question: str


# ─── 응답 ───────────────────────────────────────────────────────────────────

class TabContent(BaseModel):
    headline: str
    body: str

class ReportResponse(BaseModel):
    share_token: UUID
    feature: str
    tabs: list[TabContent]
