from pydantic import BaseModel
from typing import Optional
from enum import Enum

class IDType(str, Enum):
    COLLEGE_ID = "College ID"
    EMPLOYEE_ID = "Employee ID"
    INDUSTRY_ID = "Industry ID"

class IDInfo(BaseModel):
    name: str
    id_number: str
    organization: str
    date_of_birth: Optional[str] = None
    type: IDType = IDType.COLLEGE_ID

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Chaithanya K",
                "id_number": "123s4567A89",
                "organization": "Example University",
                "date_of_birth": "01-01-2003",
                "type": "College ID"
            }
        }