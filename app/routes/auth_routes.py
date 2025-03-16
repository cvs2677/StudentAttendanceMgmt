from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.db.dependency import db_dependency
from app.models.models import User, Token
from app.schema.token_schema import TokenResponse
from app.security.auth import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db:db_dependency):
    """
    This function handles the login process for users. It verifies the user's credentials, generates an access token,
    and stores the token in the database. If the user already has a token, it deletes the previous token.

    Parameters:
    form_data (OAuth2PasswordRequestForm): The form data containing the username and password. This is obtained from the request body.
    db (db_dependency): The database dependency, which provides a database session for interacting with the database.

    Returns:
    TokenResponse: A TokenResponse object containing the access token and token type.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"user_id": user.id, "username": user.username, "user_type": user.user_type}
    )
    db_token = Token(
        user_id = user.id,
        access_token = access_token,
        expires_at= datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    delete_previous_token= db.query(Token).filter(Token.user_id == user.id).all()
    for token in delete_previous_token:
        db.delete(token)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return TokenResponse(access_token=access_token, token_type="bearer")