from pydantic import BaseModel
from typing import Optional, List


class InjuryAnalysisRequest(BaseModel):
    user_id: str
    injury_description: Optional[str] = ""


class FirstAidStep(BaseModel):
    step_number: int
    instruction: str
    is_critical: bool = False


class InjuryAnalysisResponse(BaseModel):
    injury_type: str
    severity: str          # mild / moderate / severe
    confidence: float
    first_aid_steps: List[FirstAidStep]
    do_list: List[str]
    dont_list: List[str]
    seek_doctor: bool
    seek_doctor_reason: Optional[str] = ""
    estimated_healing: str
    warning_signs: List[str]
