from datetime import datetime
from pydantic import BaseModel



class CourseModel(BaseModel):
    course_name: str
    class_name: str
    semester: str
    lecture_hours: int
    department_id: int


class CourseResponse(CourseModel):
    id: int
    updated_at: datetime



class CourseUpdate(BaseModel):
    course_name: str = None
    class_name: str = None
    semester: str = None
    lecture_hours: int = None

    model_config = {"from_attributes": True}



