from typing import Annotated
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from functions import return_time_object, get_current_active_user, authenticate_user, create_access_token
from models import User, Token

app = FastAPI()
version_partition: str = 'v1'


# Mock database
ACCESS_TOKEN_EXPIRE_MINUTES = 30
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": True,
    },
}

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Routes / endpoints
@app.get('/')
async def root():
    return {
        'message': 'Hello World',
        'api_version': version_partition,
        'date:': return_time_object(),
    }

@app.get(f'/{version_partition}/home')
async def home():
    return {
        'message': 'Home',
        'some-data': 'Some Data',
        'date:': return_time_object(),
    }

@app.get(f'/{version_partition}/protected/home')
async def protected_home(current_user: Annotated[User, Depends(get_current_active_user)]):
    return {
        'message': 'Home',
        'some-data': 'Some Data',
        'date:': return_time_object(),
        'username': current_user.username,
        'email': current_user.email,
    }

# @app.get("/users/me")
# async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
#     return current_user

# @app.post("/token")
# async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
#     user_dict = fake_users_db.get(form_data.username)
#     if not user_dict:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#     user = UserInDB(**user_dict)
#     hashed_password = fake_hash_password(form_data.password)
#     if not hashed_password == user.hashed_password:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")

#     # This return JSON body is the required format for OAuth2. The username is just an example value, but the token_type is actual based on the bearer example.
#     return {"access_token": user.username, "token_type": "bearer"}

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, # sub "subject" of the token. It's optional, but can be used to convey credential information across systems
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user

@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]