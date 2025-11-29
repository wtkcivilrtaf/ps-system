# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import List, Optional, Any, Dict
import re

# --- Helper Functions ---
def is_password_complex(password: str) -> bool:
    if len(password) < 8: return False
    if not re.search("[a-z]", password): return False
    if not re.search("[A-Z]", password): return False
    if not re.search("[0-9]", password): return False
    return True

# --- Base Models ---
class PersonnelData(BaseModel):
    id: Optional[str] = None
    rank: str
    first_name: str
    last_name: str
    position: str
    specialty: str
    department: str

class UserData(BaseModel):
    username: str
    password: Optional[str] = None
    rank: str
    first_name: str
    last_name: str
    position: Optional[str] = ""
    department: Optional[str] = ""
    role: str

    @field_validator('username')
    def validate_username(cls, v):
        if not re.fullmatch(r"^[a-z]+$", v):
            raise ValueError("Username ต้องเป็นตัวอักษร a-z เท่านั้น")
        return v
    
    @field_validator('password')
    def validate_password_complexity(cls, v):
        if v is not None and not is_password_complex(v):
            raise ValueError("รหัสผ่านต้องมี 8 ตัว, มี a-z, A-Z, และ 0-9")
        return v

# --- Payload Models ---
class LoginPayload(BaseModel):
    username: str
    password: str

class SimpleIdPayload(BaseModel):
    id: str

class SimpleUsernamePayload(BaseModel):
    username: str

class SimpleDatePayload(BaseModel):
    date: str

class AddUserPayload(BaseModel):
    data: UserData

class UpdateUserPayload(BaseModel):
    data: UserData

class AddPersonnelPayload(BaseModel):
    data: PersonnelData

class UpdatePersonnelPayload(BaseModel):
    data: PersonnelData

class ImportPersonnelPayload(BaseModel):
    personnel: List[PersonnelData]

class StatusItem(BaseModel):
    personnel_id: str
    rank: str
    first_name: str
    last_name: str
    status: str
    details: str
    start_date: str
    end_date: str

class SubmitStatusReportPayload(BaseModel):
    report: Dict[str, Any]

class ArchiveReportPayload(BaseModel):
    reports: List[Dict[str, Any]]
    week_range: str

class DailySummaryData(BaseModel):
    officer: Dict[str, int]
    nco: Dict[str, int]
    civilian: Dict[str, int]
    total: Dict[str, int]

class DailyReportItem(BaseModel):
    personnel_id: str
    rank: str
    first_name: str
    last_name: str
    status: str
    details: str
    start_date: str
    end_date: str

class DailyReportData(BaseModel):
    officer: List[DailyReportItem]
    nco: List[DailyReportItem]
    civilian: List[DailyReportItem]

class SubmitDailyReportPayload(BaseModel):
    data: Dict[str, Any]

class ArchiveDailyReportPayload(BaseModel):
    reports: List[Dict[str, Any]]

class HolidayPayload(BaseModel):
    date: str
    description: str

class ListPayload(BaseModel):
    page: Optional[int] = 1
    searchTerm: Optional[str] = ""
    fetchAll: Optional[bool] = False
    department: Optional[str] = None