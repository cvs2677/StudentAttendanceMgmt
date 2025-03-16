from typing import List
from fastapi import APIRouter, status, HTTPException, Depends

from app.db.dependency import db_dependency
from app.models.models import Student, Department
from app.schema.student_schema import StudentModel, StudentResponse
from app.security.auth import is_admin

router = APIRouter(
    prefix="/student",
    tags=["Student"],
)


@router.post("/create-student", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(student: StudentModel, db: db_dependency, current_user=Depends(is_admin)):
    """
        Creates a new student record in the database.

        Parameters:
        - student (StudentModel): The student data to be created. This includes full_name, class_name, department_id, and submitted_by.
        - db (db_dependency): The database session dependency.
        - current_user (User, optional): The current user making the request. This is used to set the submitted_by field in the student record.

        Returns:
        - StudentResponse: The created student record.

        Raises:
        - HTTPException: If the department_id provided in the student data does not exist in the database.
        """

    department = db.query(Department).filter(Department.id == student.department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    # Create the student
    new_student = Student(
        full_name=student.full_name,
        class_name=student.class_name,
        department_id=student.department_id,
        submitted_by=current_user.id
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return StudentResponse(**new_student.__dict__)

@router.get("/students", response_model=List[StudentResponse])
async def get_students(db: db_dependency):
    """
    Get a list of students, stored in database.

    """
    students = db.query(Student).all()
    return [StudentResponse(**student.__dict__) for student in students]

@router.get("/students_by_dept_id/{department_id}")
async def get_students_by_dept_id(department_id: int, db: db_dependency):
    """
     Get the data of students for a given department

     Parameters:
     - department_id (int): The unique identifier of the department.
     - db (db_dependency): The database session dependency.

     Returns:
     - List[StudentResponse]: A list of student records belonging to the specified department.

     Raises:
     - HTTPException: If the department_id provided does not exist in the database.
     """
    existing_department = db.query(Department).filter(Department.id == department_id).first()
    if not existing_department:
        raise HTTPException(status_code=404, detail="Department not found")
    students = db.query(Student).filter(Student.department_id == department_id).all()

    return [StudentResponse(**student.__dict__) for student in students]

@router.get("/{student_id}", response_model=StudentResponse)
async def get_student_by_id(student_id: int, db: db_dependency):
    """
    Get the data of student by their student_id

    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return StudentResponse(**student.__dict__)




@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(student_id: int, student_update: StudentModel, db: db_dependency, current_user=Depends(is_admin)):
    """
       Updates an existing student record in the database.

       Parameters: - student_id (int): The unique identifier of the student to be updated. - student_update (
       StudentModel): The updated student data. This includes full_name, class_name, department_id, and submitted_by.
       - db (db_dependency): The database session dependency.
        - current_user : The current user making the request, and it can only access by the admin.


       Returns:
       - StudentResponse: The updated student record.

       Raises:
       - HTTPException: If the student_id provided does not exist in the database.
       - HTTPException: If the department_id provided in the student_update data does not exist in the database.
       """
    existing_student = db.query(Student).filter(Student.id == student_id).first()
    if not existing_student:
        raise HTTPException(status_code=404, detail="Student not found")

    existing_department = db.query(Department).filter(Department.id == student_update.department_id).first()
    if not existing_department:
        raise HTTPException(status_code=404, detail="Department not found")

    # Update the student
    update_data = student_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing_student, key, value)
    student_update.submitted_by = current_user.id

    db.commit()
    db.refresh(existing_student)

    return StudentResponse(**existing_student.__dict__)

@router.delete("/delete-student/{student_id}")
async def delete_student(student_id: int, db: db_dependency, current_user= Depends(is_admin)):
    """
    Delete a student by their student_id .
    """

    existing_student = db.query(Student).filter(Student.id == student_id).first()
    if not existing_student:
        raise HTTPException(status_code=404, detail="Student not found")

    db.delete(existing_student)
    db.commit()
    return {"detail": "Student deleted successfully"}


