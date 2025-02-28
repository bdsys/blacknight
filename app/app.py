from typing import Annotated, Any
from datetime import timedelta, date


from fastapi import Depends, FastAPI, HTTPException, status, Path, Query, Body, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse

from functions import *
from models import *

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

    # TODO remvove after creating database population script for dev environment
    if user.username == 'test':
        user.password = 'test'

    if create_user(username=user.username, email=user.email, password=user.password, user_type=user.user_type):
        print(f'User {user.username} has been created!')
    else:
        print(f'User {user.username} creation failed!')
        raise HTTPException(
            status_code=500,
            detail="An error has occured during signup. Please try again soon, sorry about that.",
        )
    
    # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # access_token = create_access_token(
    #     data={"sub": user.username}, # sub "subject" of the token. It's optional, but can be used to convey credential information across systems
    #     expires_delta=access_token_expires
    # )

    return 'OK'

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

    existing_user_value = get_user_record(current_user.username)

    json_response_body = {
        'username': existing_user_value.username,
        'email': existing_user_value.email,
        'full_name': existing_user_value.full_name,
        'user_type': existing_user_value.user_type,
        'joined': existing_user_value.joined,
        'last_updated': existing_user_value.last_updated,
        'associated_practices': existing_user_value.associated_practices,
    }

    # return current_user # too much exposed
    return json_response_body

@app.post("/users/me/password")
async def update_users_me_password(
    current_user: Annotated[UserSql, Depends(get_current_active_user)], request: Request, password: UpdatePassword,
):
    print(f'Entering POST /users/me/password')
    bearer_token_from_request_header = request.headers.get('Authorization').split('Bearer ')[1]
    print(f'Bearer token from request header: {bearer_token_from_request_header}')
    if check_jwt_blacklist(bearer_token_from_request_header):
        raise HTTPException(
            status_code=401,
            detail="Token has been invalidated",
        )

    print(f'Entering POST /users/me/password')
    print(f'User: {current_user}')
    
    password_validation_results = validate_password(password.new_password)
    if password_validation_results:
        raise HTTPException(
            status_code=400,
            detail=password_validation_results,
        )
    else:
        print(f'No password validation errors for string: {password.new_password}')

    if update_password(username=current_user.username, existing_password=password.existing_password, new_password=password.new_password):
        print(f'User {current_user.username} password has been updated!')
    else:
        print(f'User {current_user.username} password update failed!')
        raise HTTPException(
            status_code=500,
            detail="An error has occured during signup. Please try again soon, sorry about that.",
        )

    return current_user

@app.post("/users/me/type")
async def update_users_me_type(
    current_user: Annotated[UserSql, Depends(get_current_active_user)], request: Request, user_type: str, verification: bool = False,
):
    print(f'Entering POST /users/me/type')
    bearer_token_from_request_header = request.headers.get('Authorization').split('Bearer ')[1]
    print(f'Bearer token from request header: {bearer_token_from_request_header}')
    if check_jwt_blacklist(bearer_token_from_request_header):
        raise HTTPException(
            status_code=401,
            detail="Token has been invalidated",
        )

    print(f'Entering POST /users/me/type')
    print(f'User: {current_user}')
    
    if validate_user_type(user_type):
        raise HTTPException(
            status_code=400,
            detail="Invalid user type",
        )
    else:
        print(f'User type is valid: {user_type}')

    if verification:
        if update_user_type(username=current_user.username, user_type=user_type):
            print(f'User {current_user.username} user type has been updated!')
        else:
            print(f'User {current_user.username} user type update failed!')
            raise HTTPException(
                status_code=500,
                detail="An error has occured during signup. Please try again soon, sorry about that.",
            )
    else:
        raise HTTPException(
            status_code=400,
            detail="Please confirm you want to change your user type",
        )

    existing_user_value = get_user_record(current_user.username)

    json_response_body = {
        'username': existing_user_value.username,
        'email': existing_user_value.email,
        'full_name': existing_user_value.full_name,
        'user_type': existing_user_value.user_type,
        'joined': existing_user_value.joined,
        'last_updated': existing_user_value.last_updated,
        'associated_practices': existing_user_value.associated_practices,
    }

    # return current_user # too much exposed
    return json_response_body

@app.post("/users/me")
async def update_users_me(
    current_user: Annotated[UserSql, Depends(get_current_active_user)], request: Request, user: UpdateUser,
):
    print(f'Entering POST /users/me')
    bearer_token_from_request_header = request.headers.get('Authorization').split('Bearer ')[1]
    print(f'Bearer token from request header: {bearer_token_from_request_header}')
    if check_jwt_blacklist(bearer_token_from_request_header):
        raise HTTPException(
            status_code=401,
            detail="Token has been invalidated",
        )

    print(f'Entering POST /users/me')
    print(f'User: {current_user}')
    
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

    if validate_full_name(user.full_name):
        raise HTTPException(
            status_code=400,
            detail="Invalid full name",
        )
    else:
        print(f'Full name is valid: {user.full_name}')

    updated_user_value = update_user(existing_username=current_user.username, username=user.username, email=user.email, full_name=user.full_name)

    if updated_user_value:
        print(f'User {user.username} has been updated!')
    else:
        print(f'User {user.username} update failed!')
        raise HTTPException(
            status_code=500,
            detail="An error has occured during signup. Please try again soon, sorry about that.",
        )
    
    json_response_body = {
        'username': updated_user_value.username,
        'email': updated_user_value.email,
        'full_name': updated_user_value.full_name,
    }

    return json_response_body


### Practice screens
@app.get("/practices/details")
async def read_practice(current_user: Annotated[UserSql, Depends(get_current_active_user)], request: Request, practice_name: str
):
    bearer_token_from_request_header = request.headers.get('Authorization').split('Bearer ')[1]
    print(f'Bearer token from request header: {bearer_token_from_request_header}')
    if check_jwt_blacklist(bearer_token_from_request_header):
        raise HTTPException(
            status_code=401,
            detail="Token has been invalidated",
        )

    practice_value = get_practice_record(practice_name)
    if practice_value:
        json_response_body = {
            'practice_name': practice_value.practice_name,
            'practice_address': practice_value.practice_address,
            'practice_phone': practice_value.practice_phone,
            'practice_email': practice_value.practice_email,
            'practice_website': practice_value.practice_website,
            'practice_logo': practice_value.practice_logo,
            'practice_description': practice_value.practice_description,
            'practice_hours': practice_value.practice_hours,
            'practice_services': practice_value.practice_services,
            'practice_specialties': practice_value.practice_specialties,
            'practice_insurance': practice_value.practice_insurance,
            'practice_payment': practice_value.practice_payment,
            'practice_languages': practice_value.practice_languages,
        }
        return json_response_body
    else:
        raise HTTPException(
            status_code=400,
            detail="Practice does not exist",
        )

@ app.post("/practice/create")
async def create_practice(current_user: Annotated[UserSql, Depends(get_current_active_user)], request: Request, get_practice_data: GetPractice
):
    bearer_token_from_request_header = request.headers.get('Authorization').split('Bearer ')[1]
    print(f'Bearer token from request header: {bearer_token_from_request_header}')
    if check_jwt_blacklist(bearer_token_from_request_header):
        raise HTTPException(
            status_code=401,
            detail="Token has been invalidated",
        )
    
    user_type_check = get_user_record(current_user.username).user_type
    print(f'User type check: {user_type_check}')
    if user_type_check != 'practitioner':
        raise HTTPException(
            status_code=401,
            detail="User is not a practitioner",
        )

    # Validations
    validate_practice_name_return = validate_practice_name(get_practice_data.practice_name)
    if validate_practice_name_return:
        raise HTTPException(
            status_code=400,
            detail=validate_practice_name_return,
        )
    else:
        print(f'Practice name is valid: {get_practice_data.practice_name}')


    if create_practice_record(get_practice_data.practice_name):
        print(f'Practice {get_practice_data.practice_name} has been created!')
    else:
        print(f'Practice {get_practice_data.practice_name} creation failed!')
        raise HTTPException(
            status_code=500,
            detail="An error has occured during practice creation. Please try again soon, sorry about that.",
        )
    
    return 'OK'

@app.post('/practice/delete')
async def delete_practice(current_user: Annotated[UserSql, Depends(get_current_active_user)], request: Request, get_practice_data: GetPractice, verification: bool = False
):
    bearer_token_from_request_header = request.headers.get('Authorization').split('Bearer ')[1]
    print(f'Bearer token from request header: {bearer_token_from_request_header}')
    if check_jwt_blacklist(bearer_token_from_request_header):
        raise HTTPException(
            status_code=401,
            detail="Token has been invalidated",
        )

    if check_user_association_with_practice(current_user.username, get_practice_data.practice_name):
        user_type_check = get_user_record(current_user.username).user_type
        if user_type_check == 'practitioner':
            if verification:
                if delete_practice_record(get_practice_data.practice_name):
                    print(f'Practice {get_practice_data.practice_name} has been deleted!')
                    return 'OK'
                else:
                    print(f'Practice {get_practice_data.practice_name} deletion failed!')
                    raise HTTPException(
                        status_code=500,
                        detail="An error has occured during practice deletion. Please try again soon, sorry about that.",
                    )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Please confirm you want to delete this practice",
                )
        else:
            raise HTTPException(
                status_code=401,
                detail="User is not a practitioner",
            )
    else:
        raise HTTPException(
            status_code=401,
            detail="User is not associated with this practice",
        )

@app.post('/practice/update')
async def update_practice(current_user: Annotated[UserSql, Depends(get_current_active_user)], request: Request, existing_practice_name: str, practice_data: UpdatePractice
):
    print(f'Entering POST /practice/update')
    bearer_token_from_request_header = request.headers.get('Authorization').split('Bearer ')[1]
    print(f'Bearer token from request header: {bearer_token_from_request_header}')
    if check_jwt_blacklist(bearer_token_from_request_header):
        raise HTTPException(
            status_code=401,
            detail="Token has been invalidated",
        )

    if check_user_association_with_practice(current_user.username, practice_data.practice_name):
        user_type_check = get_user_record(current_user.username).user_type
        if user_type_check == 'practitioner':
            existing_practice_record = get_practice_record(existing_practice_name)
            if existing_practice_record:                
                if update_practice_record(existing_practice_record.id, practice_data):
                    print(f'Practice {practice_data.practice_name} has been updated!')

                    updated_practice_value = get_practice_record(practice_data.practice_name)
                    json_response_body = {
                        'practice_name': updated_practice_value.practice_name,
                        'practice_address': updated_practice_value.practice_address,
                        'practice_phone': updated_practice_value.practice_phone,
                        'practice_email': updated_practice_value.practice_email,
                        'practice_website': updated_practice_value.practice_website,
                        'practice_logo': updated_practice_value.practice_logo,
                        'practice_description': updated_practice_value.practice_description,
                        'practice_hours': updated_practice_value.practice_hours,
                        'practice_services': updated_practice_value.practice_services,
                        'practice_specialties': updated_practice_value.practice_specialties,
                        'practice_insurance': updated_practice_value.practice_insurance,
                        'practice_payment': updated_practice_value.practice_payment,
                        'practice_languages': updated_practice_value.practice_languages,
                    }
                    return json_response_body
                else:
                    print(f'Practice {practice_data.practice_name} update failed!')
                    raise HTTPException(
                        status_code=500,
                        detail="An error has occured during practice update. Please try again soon, sorry about that.",
                    )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Practice does not exist",
                )
        else:
            raise HTTPException(
                status_code=401,
                detail="User is not a practitioner",
            )
    else:
        raise HTTPException(
            status_code=401,
            detail="User is not associated with this practice",
        )