from pydantic import BaseModel
from typing import Optional, List


class EmergencyRequest(BaseModel):
    user_id: str
    input_text: str
    latitude: float
    longitude: float
    emergency_type: Optional[str] = "general"


class EmergencyContact(BaseModel):
    name: str
    phone: str
    relation: str


class UserContacts(BaseModel):
    user_id: str
    contacts: List[EmergencyContact]


class Hospital(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    phone: str
    specialties: List[str]
    rating: Optional[float] = 4.0
