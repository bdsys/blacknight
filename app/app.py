from typing import Annotated, Any
from datetime import timedelta, date


from fastapi import Depends, FastAPI, HTTPException, status, Path, Query, Body, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from functions import \
    return_time_object, get_current_active_user, authenticate_user, create_access_token, validate_email, validate_username, \
    username_data_dupe_check, email_data_dupe_check, validate_password, create_user, delete_user, invalidate_jwt, logout_user, \
    check_jwt_blacklist, validate_user_type, update_user
from models import Token, SignupUser, UserSql

app = FastAPI()
version_partition: str = 'v1'

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Startup tasks
# TODO - add a startup task to prune the JWT blacklist


# Routes / endpoints
## Root and home screens
@app.get('/')
async def root():
    return {
        'message': f'Blacknight API {version_partition}',
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
async def protected_home(current_user: Annotated[UserSql, Depends(get_current_active_user)], request: Request,
):
    bearer_token_from_request_header = request.headers.get('Authorization').split('Bearer ')[1]
    print(f'Bearer token from request header: {bearer_token_from_request_header}')
    if check_jwt_blacklist(bearer_token_from_request_header):
        raise HTTPException(
            status_code=401,
            detail="Token has been invalidated",
        )
    return {
        'message': 'Home',
        'some-data': 'Some Data',
        'date:': return_time_object(),
        'username': current_user.username,
        'email': current_user.email,
    }

## Authentication
@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
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

# Take a username and password in the POST body
## Validate
## Invoke token and reutrn it for login using newly created user
@app.post("/signup")
async def signup_new_user(user: SignupUser) -> str:
    
    print(f'Entering /signup')
    print(f'User: {user}')

    password_validation_results = validate_password(user.password)
    if password_validation_results:
        print(f'Password validation errors for string: {user.password}')
        raise HTTPException(
            status_code=400,
            detail=password_validation_results,
        )
    else:
        print(f'No password validation errors for string: {user.password}')

    username_validation_results = validate_username(user.username)
    if username_validation_results:
        raise HTTPException(
            status_code=400,
            detail=username_validation_results,
        )
    else:
        print(f'Username is valid: {user.username}')

    email_validation_results = validate_email(user.email)
    if email_validation_results:
        raise HTTPException(
            status_code=400,
            detail=email_validation_results,
        )
    else:
        print(f'Email is valid: {user.email}')

    if validate_user_type(user.user_type):
        raise HTTPException(
            status_code=400,
            detail="Invalid user type",
        )
    # End of all input validations

    # Duplication checks
    if username_data_dupe_check(user.username):
        # TODO we may not want to alert the user to this existing username
        raise HTTPException(
            status_code=400,
            detail="Username already registered",
        )

    if email_data_dupe_check(user.email):
        # TODO we may not want to alert the user to this existing username
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    if create_user(username=user.username, email=user.email, password=user.password, user_type=user.user_type):
        print(f'User {user.username} has been created!')
    else:
        print(f'User {user.username} creation failed!')
        raise HTTPException(
            status_code=500,
            detail="An error has occured during signup. Please try again soon, sorry about that.",
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, # sub "subject" of the token. It's optional, but can be used to convey credential information across systems
        expires_delta=access_token_expires
    )

    return access_token

# Take a username and delete + invalidate JWT
@app.delete("/users/me")
async def delete_app_user(
    current_user: Annotated[UserSql, Depends(get_current_active_user)], request: Request, verficiation: bool = False,
) -> str:

    bearer_token_from_request_header = request.headers.get('Authorization').split('Bearer ')[1]
    print(f'Bearer token from request header: {bearer_token_from_request_header}')
    if check_jwt_blacklist(bearer_token_from_request_header):
        raise HTTPException(
            status_code=401,
            detail="Token has been invalidated",
        )
    print(f'Entering DELETE /users/me')
    print(f'User: {current_user}')
    print(f'Verification: {verficiation}')
    # Verification encourages the frontend to confirm the user wants to delete their account

    if verficiation:
        bearer_token_from_request_header = request.headers.get('Authorization').split('Bearer ')[1]
        print(f'Bearer token from request header: {bearer_token_from_request_header}')
        
        if invalidate_jwt(bearer_token_from_request_header):
            print(f'JWT has been invalidated: ${bearer_token_from_request_header}')
            if delete_user(current_user.username):
                return "User has been deleted"
            else:
                print(f'JWT invalidation failed for JWT: ${bearer_token_from_request_header}')
                raise HTTPException(
                    status_code=500,
                    detail="An error has occured during deletion. Please try again soon, sorry about that.",
                )
        else:
            raise HTTPException(
                status_code=500,
                detail="An error has occured during deletion. Please try again soon, sorry about that.",
            )
    else:
        raise HTTPException(
            status_code=400,
            detail="Please confirm you want to delete your account",
        )

@app.post("/users/me/logout")
async def logout_user(
    current_user: Annotated[UserSql, Depends(get_current_active_user)], request: Request,
) -> str:
    bearer_token_from_request_header = request.headers.get('Authorization').split('Bearer ')[1]
    print(f'Bearer token from request header: {bearer_token_from_request_header}')
    if check_jwt_blacklist(bearer_token_from_request_header):
        raise HTTPException(
            status_code=401,
            detail="Token has been invalidated",
        )
    print(f'Entering /users/me/logout')
    print(f'User: {current_user}')
    bearer_token_from_request_header = request.headers.get('Authorization').split('Bearer ')[1]
    print(f'Bearer token from request header: {bearer_token_from_request_header}')
    
    if invalidate_jwt(bearer_token_from_request_header):
        print(f'JWT has been invalidated: ${bearer_token_from_request_header}')
        return "Logged out"
    else:
        print(f'JWT invalidation failed for JWT: ${bearer_token_from_request_header}')
        raise HTTPException(
            status_code=500,
            detail="An error has occured during logout. Please try again soon, sorry about that.",
        )

# ## User screens
@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[UserSql, Depends(get_current_active_user)], request: Request,
):
    bearer_token_from_request_header = request.headers.get('Authorization').split('Bearer ')[1]
    print(f'Bearer token from request header: {bearer_token_from_request_header}')
    if check_jwt_blacklist(bearer_token_from_request_header):
        raise HTTPException(
            status_code=401,
            detail="Token has been invalidated",
        )

    return current_user

@app.post("/users/me")
async def update_users_me(
    current_user: Annotated[UserSql, Depends(get_current_active_user)], request: Request, user: SignupUser,
):
    print(f'Entering POST /users/me')
    bearer_token_from_request_header = request.headers.get('Authorization').split('Bearer ')[1]
    print(f'Bearer token from request header: {bearer_token_from_request_header}')
    if check_jwt_blacklist(bearer_token_from_request_header):
        raise HTTPException(
            status_code=401,
            detail="Token has been invalidated",
        )
    
    if user.password:
        password_validation_results = validate_password(user.password)
        if password_validation_results:
            print(f'Password validation errors for string: {user.password}')
            raise HTTPException(
                status_code=400,
                detail=password_validation_results,
            )
        else:
            print(f'No password validation errors for string: {user.password}')
    else:
        print(f'No password provided for user update: {current_user.username}')
        user.password = current_user.password

    if user.username:
        username_validation_results = validate_username(user.username)
        if username_validation_results:
            raise HTTPException(
                status_code=400,
                detail=username_validation_results,
            )
        else:
            print(f'Username is valid: {user.username}')
    else:
        print(f'No username provided for user update: {current_user.username}')
        user.username = current_user.username

    if user.email:
        email_validation_results = validate_email(user.email)
        if email_validation_results:
            raise HTTPException(
                status_code=400,
                detail=email_validation_results,
            )
        else:
            print(f'Email is valid: {user.email}')
    else:
        print(f'No email provided for user update: {current_user.username}')
        user.email = current_user.email

    if user.user_type:
        if validate_user_type(user.user_type):
            raise HTTPException(
                status_code=400,
                detail="Invalid user type",
            )
    else:
        print(f'No user type provided for user update: {current_user.username}')
        user.user_type = current_user.user_type

    if update_user(username=user.username, email=user.email, password=user.password, user_type=user.user_type):
        print(f'User {user.username} has been updated!')
    else:
        print(f'User {user.username} update failed!')
        raise HTTPException(
            status_code=500,
            detail="An error has occured during signup. Please try again soon, sorry about that.",
        )

    return current_user

@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[UserSql, Depends(get_current_active_user)], request: Request,
):
    bearer_token_from_request_header = request.headers.get('Authorization').split('Bearer ')[1]
    print(f'Bearer token from request header: {bearer_token_from_request_header}')
    if check_jwt_blacklist(bearer_token_from_request_header):
        raise HTTPException(
            status_code=401,
            detail="Token has been invalidated",
        )

    return [{"item_id": "Foo", "owner": current_user.username}]

