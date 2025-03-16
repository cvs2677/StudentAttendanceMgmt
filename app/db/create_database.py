import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from app.db.database import SessionLocal
from app.models.models import User
from app.security.auth import hash_password

load_dotenv()

# Get connection details from environment variables
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Password hashing




def create_database():
    try:
        # Connect to the default "postgres" database first
        connection = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT,
        )
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()

        """Check if the database already exists"""
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"Database '{DB_NAME}' created successfully.")
        else:
            print(f"Database '{DB_NAME}' already exists.")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"An error occurred while creating the database: {e}")


def create_first_user():
    db = SessionLocal()  # Create session manually
    try:
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("A user with the username 'admin' already exists.")
            return

        data = {
            "user_type": "admin",
            "full_name": "Admin User",
            "username": "admin",
            "email": "admin@example.com",
            "password_hash": hash_password("password123"),  # Hash the password
            "submitted_by": 1
        }

        new_user = User(**data)
        db.add(new_user)
        db.commit()
        print(f'First admin user created successfully. Username - {data.get("username")}, Password - password123')

    except Exception as e:
        db.rollback()
        print(f"An error occurred while creating the admin user: {e}")

    finally:
        db.close()  # Always close the session
