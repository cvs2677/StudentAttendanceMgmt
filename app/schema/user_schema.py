from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class UserModel(BaseModel):
    user_type: str
    full_name: str
    username: str
    email: str
    password: Optional[str]=None  # ✅ Use 'password' instead of 'password_hash' (hashing happens inside the route)

class UserResponse(BaseModel):
    id: int
    user_type: str
    full_name: str
    username: str
    email: str
    submitted_by: int
    created_at: datetime

class UserUpdate(BaseModel):
    user_type: Optional[str] = None
    full_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None

    model_config = {"from_attributes": True}
