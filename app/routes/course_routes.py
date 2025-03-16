from typing import List
from fastapi import APIRouter, status, HTTPException, Depends
from app.db.dependency import db_dependency
from app.models.models import  Department, Course
from app.schema.course_schema import CourseResponse, CourseModel, CourseUpdate
from app.security.auth import is_admin

router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)

@router.post("/create_course", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(course: CourseModel, db: db_dependency, current_user=Depends(is_admin)):
    """
      Creates a new course.

      Parameters:
      - course (CourseModel): The course data to be created.
      - db (db_dependency): The database session dependency.
      - current_user : The current user making the request. Must be an admin.

      Returns:
      - CourseResponse: The created course data.

      Raises:
      - HTTPException: If the department, course name, or class name already exists.
      """


    department = db.query(Department).filter(Department.id == course.department_id).first()
    if not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")


    existing_course = db.query(Course).filter(Course.course_name == course.course_name).first()
    if existing_course:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Course already exists")

    existing_class = db.query(Course).filter(Course.class_name == course.class_name).first()
    if existing_class:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Class already exists")



    db_course = Course(**course.model_dump())
    db_course.submitted_by = current_user.id
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return CourseResponse(**db_course.__dict__)

@router.get("/get_courses", response_model=List[CourseResponse])
async def get_courses(db: db_dependency):
    """
    Get a list of courses
    """
    courses = db.query(Course).all()
    return [CourseResponse(**course.__dict__) for course in courses]

@router.get("/get_course/{course_id}", response_model=CourseResponse)
async def get_course(course_id: int, db: db_dependency):
    """
    Get a Course by course_id
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return CourseResponse(**course.__dict__)



@router.put("/update_course/{course_id}", response_model=CourseResponse)
async def update_course(course_id: int, course: CourseUpdate, db: db_dependency, current_user= Depends(is_admin)):
    """
       Updates an existing course with the provided data.

       Parameters:
       - course_id (int): The course will be updated by course_id.
       - course (CourseUpdate): The updated course data.
       - db (db_dependency): The database session dependency.
       - current_user : The current user making the request. Must be an admin.

       Returns:
       - CourseResponse: The updated course data.

       Raises:
       - HTTPException: If the course with the given course_id is not found.
       """

    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")


    update_data = course.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_course, key, value)

    db_course.submitted_by = current_user.id

    db.commit()
    db.refresh(db_course)
    return CourseResponse(**db_course.__dict__)


@router.delete("/delete_course/{course_id}", status_code=status.HTTP_200_OK)
async def delete_course(course_id: int, db: db_dependency, current_user=Depends(is_admin)):
    """
    Deletes a course by course_id.

    Parameters:
    - course_id (int): The course will be deleted by course_id.
    - db (db_dependency): The database session dependency.
    - current_user : The current user making the request. Must be an admin.

    Returns:
    - dict: A message indicating the deletion of the course.

    Raises:
    - HTTPException: If the course with the given course_id is not found.
    """

    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")


    db.delete(db_course)
    db.commit()
    return {"detail": "Course deleted successfully"}






