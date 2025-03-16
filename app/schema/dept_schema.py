from pydantic import BaseModel



class DepartmentModel(BaseModel):
    dept_name: str


class DepartmentResponse(DepartmentModel):
    id: int
    submitted_by: int

    model_config = {"form_attributes": True}

