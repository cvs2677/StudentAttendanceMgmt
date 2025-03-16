from datetime import datetime

from pydantic import BaseModel

from app.models.models import Student
from app.schema.course_schema import CourseModel
from app.schema.student_schema import StudentModel


class AttendanceModel(BaseModel):
    present: bool
    student_id: int
    course_id: int


class AttendanceResponse(AttendanceModel):
    id: int
    submitted_by: int
    updated_at: datetime

    model_config = {"from_attributes": True}

class AttendanceDetails(BaseModel):
    id: int
    present: bool
    full_name: str
    course_name: str
    class_name: str
    submitted_by: int
    updated_at: datetime



    model_config = {"from_attributes": True}







