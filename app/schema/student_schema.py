from datetime import datetime
from pydantic import BaseModel

from app.schema.dept_schema import DepartmentModel


class StudentModel(BaseModel):
    full_name: str
    class_name: str
    department_id: int


class StudentResponse(StudentModel):
    id: int
    submitted_by: int
    updated_at: datetime



    model_config = {"from_attributes": True}



