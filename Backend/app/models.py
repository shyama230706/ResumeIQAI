from pydantic import BaseModel


class ATSResponse(BaseModel):
    ats_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    suggestions: list[str]


class HealthResponse(BaseModel):
    status: str
    message: str