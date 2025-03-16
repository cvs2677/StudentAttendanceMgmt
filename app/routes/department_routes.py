from typing import List
from fastapi import APIRouter, HTTPException, status, Depends


from app.db.dependency import db_dependency
from app.models.models import  Department
from app.schema.dept_schema import DepartmentResponse, DepartmentModel
from app.security.auth import is_admin

router = APIRouter(
    prefix="/department",
    tags=["Departments"]
)

@router.get("/", response_model=List[DepartmentResponse])
async def get_departments(db: db_dependency):
    """
    Get a list of departments

    """
    departments = db.query(Department).all()

    if not departments:
        raise HTTPException(status_code=404, detail="No departments found")
    return departments






@router.post("/create_department", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(dept: DepartmentModel, db: db_dependency, current_user=Depends(is_admin)):
    """
       Creates a new department in the database.

       Parameters:
       - dept (DepartmentModel): The department data to be created.
       - db (db_dependency): The database session dependency.
       - current_user (Depends(is_admin)): The current user making the request. Must be an admin.

       Returns:
       - DepartmentResponse: The created department data.

       Raises:
       - HTTPException: If the department already exists.
       """


    existing_department = db.query(Department).filter(Department.dept_name == dept.dept_name).first()
    if existing_department:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Department already exists")

    db_department = Department(
        dept_name=dept.dept_name,
        submitted_by=current_user.id
    )
    db.add(db_department)
    db.commit()
    db.refresh(db_department)

    return DepartmentResponse(**db_department.__dict__)

@router.put("/update_dept", response_model=DepartmentResponse)
async def update_department(dept_id: int, dept: DepartmentModel,db: db_dependency, current_user= Depends(is_admin)):
    """
       Updates an existing department in the database.

       Parameters:
       - dept_id (int): The ID of the department to be updated.
       - dept (DepartmentModel): The updated department data.
       - db (db_dependency): The database session dependency.
       - current_user (Depends(is_admin)): The current user making the request. Must be an admin.

       Returns:
       - DepartmentResponse: The updated department data.

       Raises:
       - HTTPException: If the department is not found.
       """

    db_department = db.query(Department).filter(Department.id == dept_id).first()
    if not db_department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    update_data = dept.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_department, key, value)

    db_department.submitted_by = current_user.id

    db.commit()
    db.refresh(db_department)
    return DepartmentResponse(**db_department.__dict__)


@router.delete("/delete_dept/{dept_id}", status_code=status.HTTP_200_OK)
async def delete_department(dept_id: int ,db: db_dependency, current_user= Depends(is_admin)):
    """
       Deletes a department from the database.

    Parameters:
    - dept_id (int): The ID of the department to be deleted.
    - db (db_dependency): The database session dependency.
    - current_user (Depends(is_admin)): The current user making the request. Must be an admin.

    Returns:
    - dict: A success message.

    Raises:
    - HTTPException: If the department is not found.
    """

    existing_department = db.query(Department).filter(Department.id == dept_id).first()
    if not existing_department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")


    db.delete(existing_department)
    db.commit()
    return {"message": "Department deleted successfully"}






