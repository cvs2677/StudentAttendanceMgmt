
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.db.create_database import create_database, create_first_user
from app.db.database import engine, Base
from app.routes import user_routes, department_routes, student_routes, course_routes, attendance_routes, auth_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
       Asynchronous context manager for handling application lifespan.

       This function is responsible for performing startup and shutdown logic for the FastAPI application.
       During startup, it creates the database if it doesn't exist, creates tables, and creates the first admin user.
       During shutdown, it prints a message indicating that the application is shutting down.

       Parameters:
       app (FastAPI): The FastAPI application instance.

       Yields:
       None: The application runs within the context of the yield statement.

    """
    # Startup logic
    create_database()  # Create DB if it doesn’t exist
    Base.metadata.create_all(bind=engine)  # Create tables
    create_first_user()  # Create first admin user
    yield  # Application runs here
    # Shutdown logic (add if needed, e.g., closing connections)
    print("Shutting down...")

app = FastAPI(title=
              "Student Attendance Management System",
              lifespan=lifespan
              )

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(department_routes.router)
app.include_router(course_routes.router)
app.include_router(student_routes.router)
app.include_router(attendance_routes.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

