from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from app.db.dependency import db_dependency
from app.models.models import User
from app.schema.user_schema import UserResponse, UserModel, UserUpdate
from app.security.auth import hash_password, is_admin

router = APIRouter(
    prefix="/user",
    tags=["users"]
)


@router.post("/create-user", response_model=UserResponse)
async def create_user(user: UserModel, db: db_dependency, current_user =Depends(is_admin)):
    """
       Creates a new user in the system.

       Parameters:
       user (UserModel): The user data to be created. This includes user_type, full_name, username, email, and password.
       db (db_dependency): The database dependency object for interacting with the database.
       current_user (Depends(is_admin)): The currently logged-in user. This user must be an admin to perform this operation.

       Returns:
       UserResponse: The created user's data.

       Raises:
       HTTPException: If a user with the same username already exists in the system.
       """
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="User already exists.")

    db_user = User(
        user_type=user.user_type,
        full_name=user.full_name,
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),  # Hashing happens here
        submitted_by=current_user.id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return UserResponse(**db_user.__dict__)


@router.get("/all-users", response_model=List[UserResponse])
async def get_all_users(db: db_dependency):
    users = db.query(User).all()

    return  [UserResponse(**user.__dict__) for user in users]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: int, db: db_dependency):
    """
    get the user by user_id

    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(**user.__dict__)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: db_dependency, current_user =Depends(is_admin)):
    """
       Updates an existing user in the system.

       Parameters:
       user_id (int): The unique identifier of the user to be updated.
       user_update (UserUpdate): The updated user data. This includes user_type, full_name, username, email, and password.
       db (db_dependency): The database dependency object for interacting with the database.
       current_user (Depends(is_admin)): The currently logged-in user. This user must be an admin to perform this operation.

       Returns:
       UserResponse: The updated user's data.

       Raises:
       HTTPException: If the user with the given user_id does not exist in the system.
       """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    user.submitted_by = current_user.id

    db.commit()
    db.refresh(user)

    return UserResponse(**user.__dict__)

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: db_dependency, current_user= Depends(is_admin)):

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return "User deleted successfully"


