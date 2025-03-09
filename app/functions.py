from datetime import datetime, timedelta, timezone, date
from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError
import bcrypt
import os
import random
import string

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from models import *

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

def get_user_record(username: str):
    user_query = UserSql.select().where(UserSql.username == username)
    if user_query.exists():
        for user in user_query:
            return user
    else:
        return None
    
def get_practice_record(practice_name: str):
    practice_query = Practice.select().where(Practice.practice_name == practice_name)
    if practice_query.exists():
        for practice in practice_query:
            return practice
    else:
        return None

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
    
def practice_name_data_dupe_check(practice_name: str):
    practice_query = Practice.select().where(Practice.practice_name == practice_name)
    if practice_query.exists():
        print(f'Practice name {practice_name} is in SQL DB')
        for practice_name in practice_query:
            print(f'Practice name: {practice_name}')
        return True
    else:
        print(f'Practice name {practice_name} is not in SQL DB')
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
    
def check_changed_usernames(username: str):
    user_query = UserSql.select().where(UserSql.username == username)
    if user_query.exists():
        for user in user_query:
            return user
    else:
        return None
    
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
    
def validate_practice_name(practice_name: str):
    print(f'Staring practice name validation for string: {practice_name}')
    practice_name_validation_error: list[str] = []
    if practice_name:
        if len(practice_name) >= 2:
            pass
            print(f'Practice name is at least 2 characters long')
        else:
            practice_name_validation_error.append('Practice name must be at least 2 characters long')
            print(f'Practice name validation error for string: {practice_name}')
            print('Practice name must be at least 2 characters long')
        if len(practice_name) <= 50:
            pass
            print(f'Practice name is at most 50 characters long')
        else:
            practice_name_validation_error.append('Practice name cannot be any more than 50 characters long')
            print(f'Practice name validation error for string: {practice_name}')
            print('Practice name cannot be any more than 50 characters long')

        if practice_name_data_dupe_check(practice_name):
            practice_name_validation_error.append('Practice name is already in use')
            print(f'Practice name validation error for string: {practice_name}')
            print('Practice name is already in use')

        if practice_name_validation_error:
            print(practice_name_validation_error)
        else:
            print(f'No practice name validation errors for string: {practice_name}')
        return practice_name_validation_error
    
def validate_full_name(full_name: str):
    print(f'Staring full name validation for string: {full_name}')
    full_name_validation_error: list[str] = []
    if full_name:
        if len(full_name) >= 2:
            pass
            print(f'Full name is at least 2 characters long')
        else:
            full_name_validation_error.append('Full name must be at least 2 characters long')
            print(f'Full name validation error for string: {full_name}')
            print('Full name must be at least 2 characters long')
        if len(full_name) <= 50:
            pass
            print(f'Full name is at most 50 characters long')
        else:
            full_name_validation_error.append('Full name cannot be any more than 50 characters long')
            print(f'Full name validation error for string: {full_name}')
            print('Full name cannot be any more than 50 characters long')

        if full_name_validation_error:
            print(full_name_validation_error)
        else:
            print(f'No full name validation errors for string: {full_name}')
        return full_name_validation_error
    
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
            print('User type must be either "user" or "practitioner')
        if user_type_validation_error:
            print(user_type_validation_error)
        else:
            print(f'No user type validation errors for string: {user_type}')
        return user_type_validation_error    
    
def validate_practice_association_type(association_type: str):
    print(f'Staring association type validation for string: {association_type}')
    association_type_validation_error: list[str] = []
    if association_type:
        if association_type in ['owner', 'member', 'provider']:
            pass
            print(f'Association type is valid')
        else:
            association_type_validation_error.append('Association type must be either "owner", "member" or "provider"')
            print(f'Association type validation error for string: {association_type}')
            print('Association type must be either "owner", "member" or "provider')
        if association_type_validation_error:
            print(association_type_validation_error)
        else:
            print(f'No association type validation errors for string: {association_type}')
        return association_type_validation_error

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
    print(f'debug -- creating user with data:')
    print(f'username: {username}')
    print(f'email: {email}')
    print(f'hashed_password: {hashed_password}')
    print(f'user_type: {user_type}')
    new_user = UserSql(
        username=username,
        email=email,
        joined=date.today(),
        disabled=False,
        hashed_password=hashed_password,
        user_type=user_type,
    )
    if new_user.save() == 1:
        print(f'User {username} has been saved to SQL DB')
        return True
    else:
        print(f'User {username} has not been saved to SQL DB')
        return False
    
def create_practice_record(practice_name: str):
    new_practice = Practice(
        practice_name=practice_name,
        created = date.today(),
    )
    if new_practice.save() == 1:
        print(f'Practice {practice_name} has been saved to SQL DB')
        return True
    else:
        print(f'Practice {practice_name} has not been saved to SQL DB')
        return False
    
def update_user(existing_username: str, username: str, email: str, full_name: str):

    # Getting a user to read some data. Couldn't get this to work for updating existing records
    # existing_user = UserSql.select().where(UserSql.username == existing_username).get()
    # existing_user = UserSql.get(UserSql.username == existing_username)
    # grandma = Person.select().where(Person.name == 'Grandma L.').get()
    # grandma = Person.get(Person.name == 'Grandma L.')

    # Updating a record by specifying which columns to update, then which user to update then executing the query
    # update_query = Entry.update(published=True).where(pub_date__lt=datetime.today())
    # update_query.execute()
    update_existing_user = UserSql.update(
        username=username,
        email=email,
        full_name=full_name,
        last_updated=date.today(),
    ).where(UserSql.username == existing_username)
    execute_update = update_existing_user.execute()

    # if existing_user.save() == 1:
    if execute_update:
        print(f'User {username} has been saved to SQL DB')
        return get_user_record(username)
    else:
        print(f'User {username} has not been saved to SQL DB')
        return None
    
def update_practice_record(existing_practice_id: int, practice: UpdatePractice):
    update_existing_practice = Practice.update(
        practice_name=practice.practice_name,
        practice_address=practice.practice_address,
        practice_phone=practice.practice_phone,
        practice_email=practice.practice_email,
        practice_website=practice.practice_website,
        practice_logo=practice.practice_logo,
        practice_description=practice.practice_description,
        practice_hours=practice.practice_hours,
        practice_services=practice.practice_services,
        practice_specialties=practice.practice_specialties,
        practice_insurance=practice.practice_insurance,
        practice_payment=practice.practice_payment,
        practice_languages=practice.practice_languages,
    ).where(Practice.id == existing_practice_id,)
    execute_update = update_existing_practice.execute()
    if execute_update:
        print(f'Practice {practice.practice_name} has been updated')
        return True
    else:
        print(f'Practice {practice.practice_name} has not been updated')
        return False

def update_password(username: str, existing_password: str, new_password: str):
    # Check if the existing password matches the one in the database
    if verify_password(existing_password, UserSql.hashed_password):
        # If it matches, hash the new password and update the user record
        hashed_new_password = get_password_hash(new_password)
        update_existing_password = UserSql.update(
            hashed_password=hashed_new_password,
            last_updated=date.today(),
        ).where(UserSql.username == username)
        execute_update = update_existing_password.execute()
        if execute_update:
            print(f'Password has been updated')
            return True
        else:
            print(f'Password has not been updated')
            return False
    else:
        print(f'Password does not match')
        return False
    
def update_user_type(username: str, user_type: str):
    update_existing_user_type = UserSql.update(
        user_type=user_type,
        last_updated=date.today(),
    ).where(UserSql.username == username)
    execute_update = update_existing_user_type.execute()
    if execute_update:
        print(f'User type has been updated')
        return True
    else:
        print(f'User type has not been updated')
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
    
def delete_practice_record(practice_name: str):
    if get_practice_record(practice_name):
        practice_id = Practice.select(Practice.id).where(Practice.practice_name == practice_name)
        practice_id = practice_id.get()
        if practice_id:
            practice_id.delete_instance()
            print(f'Practice {practice_name} has been deleted from SQL DB')
    
        UserToPractice.delete().where(UserToPractice.practice == practice_id).execute()
        print('All users associated with this practice have been deleted')
        return True
    
    else:
        print(f'Practice {practice_name} does not exist in SQL DB')
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
        print(f'JWT {jwt} is in blacklist SQL DB')
        for jwt in jwt_query:
            print(f'JWT: {jwt}')
        return True
    else:
        print(f'JWT {jwt} is not in blacklist SQL DB')
        return False

def logout_user(jwt: str):
    if invalidate_jwt(jwt):
        print(f'User has been logged out')
        return True
    else:
        print(f'User has not been logged out')
        return False
    
def add_user_to_practice(username: str, practice_name: str, association: str='member'):
    user = get_user_record(username)
    practice = get_practice_record(practice_name)
    if user and practice:
        
        print(f'Adding user to UserToPractice table with data:')
        print(f'User: {user}')
        print(f'Practice: {practice}')
        print(f'association_type: {association}')
        user_to_practice_association = UserToPractice(
            user=user,
            practice=practice,
            created = date.today(),
            association_type=association
        )

        if user_to_practice_association.save() == 1:
            print(f'User {username} has been added to practice {practice_name}')
            return None
        else:
            print(f'User {username} has not been added to practice {practice_name}')
            return f'User {username} has not been added to practice {practice_name}'
    else:
        print(f'User {username} or practice {practice_name} does not exist in SQL DB')
        return f'User {username} or practice {practice_name} does not exist in SQL DB'
    
def disassociate_user_from_practice(username: str, practice_name: str):
    user = get_user_record(username)
    practice = get_practice_record(practice_name)
    if user and practice:
        user_to_practice_association = UserToPractice.select().where((UserToPractice.user == user) & (UserToPractice.practice == practice))
        if user_to_practice_association.exists():
            user_to_practice_association.get().delete_instance()
            print(f'User {username} has been removed from practice {practice_name}')
            return f'User {username} has been removed from practice {practice_name}'
        else:
            print(f'User {username} is not associated with practice {practice_name}')
            return f'User {username} is not associated with practice {practice_name}'
    else:
        print(f'User {username} or practice {practice_name} does not exist in SQL DB')
        return f'User {username} or practice {practice_name} does not exist in SQL DB'

def check_user_association_with_practice(username: str, practice_name: str):

    user_record = get_user_record(username)
    practice_record = get_practice_record(practice_name)

    if practice_record and user_record:
        associated_users_query= (UserSql.select()
            .join(UserToPractice, on=UserToPractice.user)
            .where((UserToPractice.practice == practice_record) & (UserToPractice.user == user_record))
            .order_by(UserSql.username))

        if associated_users_query.exists():
            for user in associated_users_query:
                if user.username == username:
                    print(f'User {username} is associated with practice {practice_name}')
                    return True
                    # return False
            print(f'User {username} is not associated with practice {practice_name}')
            return False
        else:
            print(f'No users are associated with practice {practice_name}')
            return False
        
def check_user_owner_of_practice(username: str, practice_name: str):
    user_record = get_user_record(username)
    practice_record = get_practice_record(practice_name)

    if practice_record and user_record:
        user_to_practice_association = UserToPractice.select().where((UserToPractice.user == user_record) & (UserToPractice.practice == practice_record))
        if user_to_practice_association.exists():
            user_to_practice_association_row = user_to_practice_association.get()
            if user_to_practice_association_row.association_type == 'owner':
                print(f'User {username} is an owner of practice {practice_name}')
                return True
            else:
                print(f'User {username} is not an owner of practice {practice_name}')
                return False
        else:
            print(f'User {username} is not associated with practice {practice_name}')
            return False

def get_associated_users_from_practice(practice_name: str):
    practice = get_practice_record(practice_name)
    if practice:
        associated_users_query= (UserSql.select()
            .join(UserToPractice, on=UserToPractice.user)
            .where(UserToPractice.practice == practice)
            .order_by(UserSql.username))

        associated_usernames = []
        if associated_users_query.exists():
            for user in associated_users_query:
                associated_usernames.append(user.username)
        else:
            print(f'No users are associated with practice {practice_name}')
            associated_usernames.append('No users are associated with this practice')

        return associated_usernames
    else:
        print(f'Practice {practice_name} does not exist in SQL DB')
        return None

def change_user_association_with_practice(username_to_modify: str, practice_name: str, association_type: str):
    user = get_user_record(username_to_modify)
    practice = get_practice_record(practice_name)
    if user and practice:
        user_to_practice_association = UserToPractice.select().where((UserToPractice.user == user) & (UserToPractice.practice == practice))
        if user_to_practice_association.exists():            
            user_to_practice_association_row = user_to_practice_association.get()
            user_to_practice_association_row.association_type = association_type
            user_to_practice_association_row.save()
            print(f'User {username_to_modify} is now a {association_type} of practice {practice_name}')
            return f'User {username_to_modify} is now a {association_type} of practice {practice_name}'
        else:
            print(f'User {username_to_modify} is not associated with practice {practice_name}')
            return f'User {username_to_modify} is not associated with practice {practice_name}'
    else:
        print(f'User {username_to_modify} or practice {practice_name} does not exist in SQL DB')
        return f'User {username_to_modify} or practice {practice_name} does not exist!'

def generate_unique_join_code(join_codes_constraint: list[str], min: int, max: int):
    # Example for generating a random string of 12 uppercase characters + digits
    # join_code_1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

    # Generated 5 digits for join codes
    join_code = random.randint(min,max)
    # print(f'Generated join code: {join_code}')
    while join_code in join_codes_constraint:
        # print(f'Generated join code: {join_code} is not unique')
        join_code = random.randint(min,max)
    return join_code

def create_practice_join_codes(practice_name: str):
    practice = get_practice_record(practice_name)
    if practice:
        
        generated_codes = []
        for i in range(5):
            generated_codes.append(generate_unique_join_code(generated_codes, 10000, 99999))

        print(f'Generated join codes: {generated_codes}')

        new_practice_join_codes = PracticeJoinCodes(
            practice=practice,
            join_code_1=generated_codes[0],
            join_code_2=generated_codes[1],
            join_code_3=generated_codes[2],
            join_code_4=generated_codes[3],
            join_code_5=generated_codes[4],
            created=datetime.now(),
        )

        if new_practice_join_codes.save() == 1:
            print(f'Join codes for practice {practice_name} have been saved to SQL DB')
            return True
        else:
            print(f'Join codes for practice {practice_name} have not been saved to SQL DB')
            return False
    else:
        print(f'Practice {practice_name} does not exist in SQL DB')
        return False
    
def get_practice_join_codes(practice_name: str):
    practice = get_practice_record(practice_name)
    if practice:
        join_codes_query = PracticeJoinCodes.select().where(PracticeJoinCodes.practice == practice)
        if join_codes_query.exists():
            for join_codes in join_codes_query:
                join_codes_dict = {
                    'join_code_1': join_codes.join_code_1,
                    'join_code_2': join_codes.join_code_2,
                    'join_code_3': join_codes.join_code_3,
                    'join_code_4': join_codes.join_code_4,
                    'join_code_5': join_codes.join_code_5,
                }
                return join_codes_dict
        else:
            print(f'No join codes for practice {practice_name} in SQL DB')
            return None
    else:
        print(f'Practice {practice_name} does not exist in SQL DB')
        return None
    
def validate_join_code(join_code: int, practice_name: str):
    practice = get_practice_record(practice_name)
    if practice:
        join_codes_query = PracticeJoinCodes.select().where(PracticeJoinCodes.practice == practice)
        join_code_row = join_codes_query.get()
        # print(join_code_row)
        
        join_codes = [
            join_code_row.join_code_1,
            join_code_row.join_code_2,
            join_code_row.join_code_3,
            join_code_row.join_code_4,
            join_code_row.join_code_5,
        ]

        # print(f'Checking if {join_code} is in {join_codes}')
        if join_code in join_codes:
            print(f'Join code {join_code} is valid')
            return True
        else:
            print(f'Join code: {join_code} is invalid for practice: {practice_name}.')
            return False
    else:
        print(f'Practice {practice_name} does not exist in SQL DB')
        return False
    
def get_user_to_practice_association_type(username: str, practice_name: str):
    user = get_user_record(username)
    practice = get_practice_record(practice_name)
    # print(f'Getting user type for user {user} and practice {practice}')
    if user and practice:
        user_to_practice_association = UserToPractice.select().where((UserToPractice.user == user) & (UserToPractice.practice == practice))
        if user_to_practice_association.exists():
            user_to_practice_association_row = user_to_practice_association.get()
            return user_to_practice_association_row.association_type
        else:
            print(f'User {username} is not associated with practice {practice_name}')
            return None
    else:
        print(f'User {username} or practice {practice_name} does not exist in SQL DB')
        return None

def create_user_isi_data(username: str, date_start: date, date_end: date, score: int):


    # TODO refactor this to update if date exists or create
    # Works with Postgresql and SQLite (which supports ON CONFLICT ... UPDATE).
    # result = (Emp
    #         .insert(first='foo', last='bar', empno='125')
    #         .on_conflict(
    #             conflict_target=(Emp.empno,),
    #             preserve=(Emp.first, Emp.last),
    #             update={Emp.empno: '125.1'})
    #         .execute())

    user = get_user_record(username)
    if user:
        new_isi_data = IsiData(
            user=user,
            date_start=date_start,
            date_end=date_end,
            score=score,
            last_updated_by=user,
            last_updated=datetime.now(),
            associated_practice=None
        )

        if new_isi_data.save() == 1:
            print(f'ISI data for user {username} has been saved to SQL DB')
            return True
        else:
            print(f'ISI data for user {username} has not been saved to SQL DB')
            return False
    else:
        print(f'User {username} does not exist in SQL DB')
        return False
