from datetime import datetime, timedelta, timezone, date
from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError
import bcrypt
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from models import TokenData, UserSql, BlackListedJwt

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Mock database
# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "6208de85fc9b7794731ae49e88745ad853d2043b9f0b31ae6e21909bd3457313"
ALGORITHM = "HS256"
# SECRET_KEY = os.environ.get('SECRET_KEY')
# ALGORITHM = os.environ.get('ALGORITHM')
bcrypt_salt = bcrypt.gensalt()

def return_time_object():
    return datetime.now()
    
def get_user(username: str):
    user_query = UserSql.select().where(UserSql.username == username)
    if user_query.exists():
        for user in user_query:
            return user
    else:
        return None

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub") # sub "subject" of the token. It's optional, but can be used to convey credential information across systems
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[UserSql, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8'),
    )

def get_password_hash(password):
    # Returns a hashed password using bcrypt salt
    return bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt_salt,
    )

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def username_data_dupe_check(username: str):
    # query for user with username or email
    user_query = UserSql.select().where(UserSql.username == username)
    if user_query.exists():
        print(f'Username {username} is in SQL DB')
        for username in user_query:
            print(f'Username: {username}')
        return True
    else:
        print(f'Username {username} is not in SQL DB')
        return False

def email_data_dupe_check(email: str):
    email_query = UserSql.select().where(UserSql.email == email)
    if email_query.exists():
        print(f'Email {email} is in SQL DB')
        for email in email_query:
            print(f'Email: {email}')
        return True
    else:
        print(f'Email {email} is not in SQL DB')
        return False
    
def validate_username(username: str):
    print(f'Staring username validation for string: {username}')
    username_validation_error: list[str] = []
    if username:
        if len(username) >= 4:
            pass
            print(f'Username is at least 4 characters long')
        else:
            username_validation_error.append('Username must be at least 4 characters long')
            print(f'Username validation error for string: {username}')
            print('Username must be at least 4 characters long')
        if len(username) <= 20:
            pass
            print(f'Username is at most 20 characters long')
        else:
            username_validation_error.append('Username cannot be any more than 20 characters long')
            print(f'Username validation error for string: {username}')
            print('Username cannot be any more than 20 characters long')

        if username_validation_error:
            print(username_validation_error)
        else:
            print(f'No username validation errors for string: {username}')
        return username_validation_error
    
def validate_email(email: str):
    print(f'Staring email validation for string: {email}')
    email_validation_error: list[str] = []
    if email:
        if '@' in email:
            pass
            print(f'Email has an "@" character')
        else:
            email_validation_error.append('Email must have an "@" character')
            print(f'Email validation error for string: {email}')
            print('Email must have an "@" character')
        if '.' in email:
            pass
            print(f'Email has a "." character')
        else:
            email_validation_error.append('Email must have a "." character')
            print(f'Email validation error for string: {email}')
            print('Email must have a "." character')
        if email.split('.')[-1] in ['com', 'net', 'org']:
            pass
            print(f'Email has a valid domain')
        else:
            email_validation_error.append('Email must have a valid domain. e.g. com, net, org')
            print(f'Email validation error for string: {email}')
            print('Email must have a valid domain')
        if email_validation_error:
            print(email_validation_error)
        else:
            print(f'No email validation errors for string: {email}')
        return email_validation_error

def validate_user_type(user_type: str):
    print(f'Staring user type validation for string: {user_type}')
    user_type_validation_error: list[str] = []
    if user_type:
        if user_type in ['user', 'practitioner']:
            pass
            print(f'User type is valid')
        else:
            user_type_validation_error.append('User type must be either "user" or "practitioner"')
            print(f'User type validation error for string: {user_type}')
            print('User type must be either "user" or "admin')
        if user_type_validation_error:
            print(user_type_validation_error)
        else:
            print(f'No user type validation errors for string: {user_type}')
        return user_type_validation_error    

def validate_password(password: str):
    print(f'Staring password validation for string: {password}')
    password_validation_error: list[str] = []
    if password:
        if any(not c.isalnum() for c in password): # Check if password has at least one non-alphanumeric character
            pass
            print('Password has at least one non-alphanumeric character')
        else:
            password_validation_error.append('Password must have at least one non-alphanumeric character')
            print(f'Password validation error for string: {password}')
            print('Password must have at least one non-alphanumeric character')

        if any(c.isupper() for c in password):
            pass
            print(f'Password has at least one uppercase character')
        else:
            password_validation_error.append('Password must have at least one uppercase character')
            print(f'Password validation error for string: {password}')
            print('Password must have at least one uppercase character')

        if any(c.islower() for c in password):
            pass
            print(f'Password has at least one lowercase character')
        else:
            password_validation_error.append('Password must have at least one lowercase character')
            print(f'Password validation error for string: {password}')
            print('Password must have at least one lowercase character')

        if any(c.isdigit() for c in password):
            pass
            print(f'Password has at least one digit')
        else:
            password_validation_error.append('Password must have at least one digit')
            print(f'Password validation error for string: {password}')
            print('Password must have at least one digit')

        if len(password) >= 8:
            pass
            print(f'Password is at least 8 characters long')
        else:
            password_validation_error.append('Password must be at least 8 characters long')
            print(f'Password validation error for string: {password}')
            print('Password must be at least 8 characters long')

        if len(password) <= 20:
            pass
            print(f'Password is at most 20 characters long')
        else:
            password_validation_error.append('Password cannot be any more than 20 characters long')
            print(f'Password validation error for string: {password}')
            print('Password cannot be any more than 20 characters long')

        # List contains at least one error message
        if password_validation_error:
            print(password_validation_error)
        else:
            print(f'No password validation errors for string: {password}')

        return password_validation_error
    
def create_user(username: str, email: str, password: str, user_type: str):
    hashed_password = get_password_hash(password)
    new_user = UserSql(
        username=username,
        email=email,
        joined=date.today(),
        disabled=False,
        hashed_password=hashed_password,
        type=user_type,
    )
    if new_user.save() == 1:
        print(f'User {username} has been saved to SQL DB')
        return True
    else:
        print(f'User {username} has not been saved to SQL DB')
        return False
    
def update_user(username: str, email: str, password: str, user_type: str):
    hashed_password = get_password_hash(password)
    existing_user_lookup = UserSql.select(UserSql.id).where(UserSql.username == username)
    existing_user = existing_user_lookup.get()

    existing_user.username=username,
    existing_user.email=email,
    existing_user.last_updated=date.today(),
    existing_user.disabled=False,
    existing_user.hashed_password=hashed_password,
    existing_user.type=user_type,

    if existing_user.save() == 1:
        print(f'User {username} has been saved to SQL DB')
        return True
    else:
        print(f'User {username} has not been saved to SQL DB')
        return False

def delete_user(username: str):
    user_id = UserSql.select(UserSql.id).where(UserSql.username == username)
    user_id = user_id.get()
    if user_id:
        user_id.delete_instance()
        print(f'User {username} has been deleted from SQL DB')
        return True
    else:
        print(f'User {username} has not been deleted from SQL DB')
        return False
    
def invalidate_jwt(jwt: str):
    if check_jwt_blacklist(jwt):
        print(f'JWT {jwt} is already blacklisted')
        return True

    new_blacklisted_jwt = BlackListedJwt(
        jwt=jwt,
        created=datetime.now(),
    )

    if new_blacklisted_jwt.save() == 1:
        print(f'JWT {jwt} has been saved to SQL DB')
        return True
    else:
        print(f'JWT {jwt} has not been saved to SQL DB')
        return False
    
def check_jwt_blacklist(jwt: str):
    jwt_query = BlackListedJwt.select().where(BlackListedJwt.jwt == jwt)
    if jwt_query.exists():
        print(f'JWT {jwt} is in SQL DB')
        for jwt in jwt_query:
            print(f'JWT: {jwt}')
        return True
    else:
        print(f'JWT {jwt} is not in SQL DB')
        return False

def logout_user(jwt: str):
    if invalidate_jwt(jwt):
        print(f'User has been logged out')
        return True
    else:
        print(f'User has not been logged out')
        return False
