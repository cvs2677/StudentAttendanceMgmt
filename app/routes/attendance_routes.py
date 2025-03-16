from typing import List

from fastapi import APIRouter, HTTPException, status, Depends

from app.db.dependency import db_dependency
from app.models.models import Student, Course, AttendanceLog
from app.schema.attendance_schema import AttendanceResponse, AttendanceModel, AttendanceDetails
from app.security.auth import is_admin_or_teacher

router = APIRouter(
    prefix="/attendance",
    tags=["AttendanceLog"]
)

@router.post("/create_attendance", response_model=AttendanceResponse)
async def create_attendance(attendance_log: AttendanceModel, db: db_dependency, current_user = Depends(is_admin_or_teacher)):
    """
    Creates a new attendance log.

    Parameters:
    attendance_log (AttendanceModel): The attendance log data to be created.
    db (db_dependency): The database session dependency.
    current_user (User): The current user making the request. This is obtained using the is_admin_or_teacher dependency.

    Returns:
    AttendanceResponse: The created attendance log.

    Raises:
    HTTPException: If the course or student does not exist, or if an attendance log for the given course, student, and date already exists.
    """

    course = db.query(Course).filter(Course.id == attendance_log.course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")

    student = db.query(Student).filter(Student.id == attendance_log.student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")

    existing_attendance = db.query(AttendanceLog).filter(
        AttendanceLog.course_id == attendance_log.course_id,
        AttendanceLog.student_id == attendance_log.student_id,
      ).first()

    if existing_attendance:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Attendance log for the given course, student, and date already exists.")

    db_attendance = AttendanceLog(**attendance_log.model_dump())

    db_attendance.submitted_by = current_user.id

    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)

    return AttendanceResponse(**db_attendance.__dict__)

@router.get("/get_attendance_logs", response_model=List[AttendanceDetails])
async def get_attendance_logs(db: db_dependency):
    """
    Retrieves a list of attendance logs.
    """

    attendance_logs = (db.query(
            AttendanceLog.id,
            AttendanceLog.present,
            AttendanceLog.updated_at,
            AttendanceLog.submitted_by,
            Student.full_name,
            Course.course_name,
            Course.class_name)
            .join(Student, AttendanceLog.student_id == Student.id)
            .join(Course, AttendanceLog.course_id == Course.id).all())
    return attendance_logs