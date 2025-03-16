from datetime import datetime, timezone

from sqlalchemy.orm import relationship

from app.db.database import Base
from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP, ForeignKey


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_type = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))

    creator = relationship("User", back_populates="created_users", remote_side=[id])
    created_users = relationship("User", back_populates="creator")

    tokens = relationship("Token", back_populates="user")


class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    dept_name = Column(String, nullable=False, unique=True)
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    courses = relationship("Course", back_populates="department")
    students = relationship("Student", back_populates="department")


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    class_name = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_at = Column(
        TIMESTAMP,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    department = relationship("Department", back_populates="students")
    attendance_logs = relationship("AttendanceLog", back_populates="student")


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, nullable=False, unique=True)
    class_name = Column(String, nullable=False)
    semester = Column(String, nullable=False)
    lecture_hours = Column(Integer, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_at = Column(
        TIMESTAMP,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    department = relationship("Department", back_populates="courses")
    attendance_logs = relationship("AttendanceLog", back_populates="course")


class AttendanceLog(Base):
    __tablename__ = "attendance_logs"
    id = Column(Integer, primary_key=True, index=True)
    present = Column(Boolean, nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_at = Column(
        TIMESTAMP,
        default=datetime.now(timezone.utc)
    )

    student = relationship("Student", back_populates="attendance_logs")
    course = relationship("Course", back_populates="attendance_logs")


class Token(Base):
    __tablename__ = 'tokens'
    token_id = Column(Integer, primary_key=True, index=True)
    access_token = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    expires_at = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now(timezone.utc))

    user = relationship("User", back_populates="tokens")