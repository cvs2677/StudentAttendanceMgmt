from datetime import timedelta, datetime, timezone
from fastapi import HTTPException, status, Depends
from typing import Optional, Annotated
from dotenv import load_dotenv
import os
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.db.dependency import db_dependency
from app.models.models import User, Token

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

def hash_password(password:str) -> str:
    """
    Hashes the provided password using the bcrypt algorithm.

    Parameters:
    - password (str): The password to be hashed.

    returns:
    - str: The hashed password.
    """
    return pwd_context.hash(password)

def verify_password(password, hashed_password):
    """
    Verifies if the provided password matches the hashed password using the CryptContext library.

    """
    return pwd_context.verify(password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta]=None) -> str:
    """
    This function generates a JWT access token for a user based on the provided data and expiration delta.

    Parameters:
    - data (dict): A dictionary containing the user's information to be encoded in the JWT token.
        It should contain at least the following keys: 'user_id', 'username', and 'user_type'.
    - expires_delta (Optional[timedelta]): An optional parameter specifying the duration for which the token should be valid.
        If not provided, the token will expire after a default duration specified by the ACCESS_TOKEN_EXPIRE_MINUTES environment variable.

    Returns:
    - str: The generated JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, db: db_dependency) -> dict:
    """
    Verifies the JWT token and retrieves user information from the database.

    Parameters:
    - token (str): The JWT token provided by the client. This token is used to authenticate the user.
    - db (db_dependency): The database dependency object for querying the database.

    Returns:
    - dict: A dictionary containing the user's ID, username, and user type if the token is valid and the user exists in the database.

    Raises:
    - HTTPException: If the token is invalid or expired, it raises an HTTPException with a 401 status code and a message indicating "Invalid Token" or "Invalid or expired Token".
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        username = payload.get("username")
        user_type = payload.get("user_type")

        if not user_id or not username or not user_type:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

        access = db.query(Token).filter(Token.user_id == user_id).first()
        if access.access_token != token or access.expires_at < datetime.now():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired Token")

        return {"user_id": user_id, "username": username, "user_type": user_type}

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired Token")

def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: db_dependency) -> User:
    """
    This function retrieves the current user based on the provided token and database dependency.

    Parameters:
    - token (Annotated[str, Depends(oauth2_bearer)]): The JWT token provided by the client. This token is used to authenticate the user.
    - db (db_dependency): The database dependency object for querying the database.

    Returns:
    - User: The current user object if the token is valid and the user exists in the database.

    Raises:
    - HTTPException: If the token is invalid or expired, it raises an HTTPException with a 401 status code and a message indicating "Could not validate credentials".
    - HTTPException: If the user does not exist in the database, it raises an HTTPException with a 403 status code and a message indicating "Invalid User".
    """
    payload = verify_token(token, db)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user =  db.query(User).filter(User.id == payload["user_id"]).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid User")

    return user


def is_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    """
    This function checks if the user is an admin. If the user is not an admin, it raises an HTTPException with a 403 status code.

    Parameters:
    - user (Annotated[User, Depends(get_current_user)]): The current user object obtained from the `get_current_user` function.
        This parameter is annotated with `Annotated` and `Depends` to indicate that it is a dependency that needs to be resolved.

    Returns:
    - The user object if the user is an admin.

    Raises:
    - HTTPException: If the user is not an admin, it raises an HTTPException with a 403 status code and a message indicating "Unauthorized Access!".
    """
    if user.user_type != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized Access!")

    return user


def is_admin_or_teacher(user: Annotated[User, Depends(get_current_user)]):
    """
    This function checks if the user is an admin or a teacher. If not, it raises an HTTPException with a 403 status code.

    Parameters:
    - user (Annotated[User, Depends(get_current_user)]): The current user object obtained from the `get_current_user` function.
    - db (db_dependency): The database dependency object for querying the database.

    Returns:
    - The user object if the user is an admin or a teacher.

    Raises:
    - HTTPException: If the user is not an admin or a teacher, it raises an HTTPException with a 403 status code and a message indicating "Admin or Teacher Required".
    """
    if user.user_type not in ["admin", "teacher"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access")
    return user





