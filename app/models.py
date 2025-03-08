from typing import Annotated, Literal
from pydantic import BaseModel
from fastapi import Depends
from peewee import *
from datetime import date

# Data models
class SignupUser(BaseModel):
    username: str
    email: str
    password: str
    user_type: Literal['user', 'practitioner'] = 'user'

class UpdateUser(BaseModel):
    username: str
    email: str
    full_name: str

class UpdateUserType(BaseModel):
    user_type: Literal['user', 'practitioner'] = 'user'

class UpdatePassword(BaseModel):
    existing_password: str
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class GetPractice(BaseModel):
    practice_name: str

class UpdatePractice(BaseModel):
    practice_name: str
    practice_address: str | None = None
    practice_phone: str | None = None
    practice_email: str | None = None
    practice_website: str | None = None
    practice_logo: str | None = None
    practice_description: str | None = None
    practice_hours: str | None = None
    practice_services: str | None = None
    practice_specialties: str | None = None
    practice_insurance: str | None = None
    practice_payment: str | None = None
    practice_languages: str | None = None

class CreateIsiData(BaseModel):
    username: str
    start_date: date
    end_date: date
    score: int

# SQL models -- peewee
db = SqliteDatabase('database.db')
## Classes

class UserSql(Model):
    id = AutoField()
    username = CharField(unique=True)
    email = CharField(unique=True)
    full_name = CharField(null=True)
    joined = DateField()
    last_updated = DateField(default=date.today)
    disabled = BooleanField(default=True)
    hashed_password = CharField()
    user_type = CharField(choices=[('user', 'User'), ('admin', 'Admin')], default='user')

    class Meta:
        database = db

class Practice(Model):
    id = AutoField()
    created = DateTimeField()
    last_updated = DateField(default=date.today)
    practice_name = CharField(null=True)
    practice_address = CharField(null=True)
    practice_phone = CharField(null=True)
    practice_email = CharField(null=True)
    practice_website = CharField(null=True)
    practice_logo = CharField(null=True)
    practice_description = TextField(null=True)
    practice_hours = CharField(null=True)
    practice_services = TextField(null=True)
    practice_specialties = TextField(null=True)
    practice_insurance = TextField(null=True)
    practice_payment = TextField(null=True)
    practice_languages = TextField(null=True)
    # associated_users = ForeignKeyField(UserSql, backref='practices', null=True)

    class Meta:
        database = db

class PracticeJoinCodes(Model):
    id = AutoField()
    practice = ForeignKeyField(Practice, backref='join_codes')
    join_code_1 = CharField(unique=True)
    join_code_2 = CharField(unique=True)
    join_code_3 = CharField(unique=True)
    join_code_4 = CharField(unique=True)
    join_code_5 = CharField(unique=True)
    created = DateTimeField()

    class Meta:
        database = db

class UserToPractice(Model):
    id = AutoField()
    user = ForeignKeyField(UserSql)
    practice = ForeignKeyField(Practice)
    created = DateTimeField()
    association_type = CharField(choices=[('owner', 'Owner'), ('member', 'Member')], default='member')

    class Meta:
        # CompositeKey('user', 'practice')
        database = db

class BlackListedJwt(Model):
    id = AutoField()
    jwt = CharField(unique=True)
    created = DateTimeField()

    class Meta:
        database = db

class SleepData(Model):
    id = AutoField()
    user = ForeignKeyField(UserSql, backref='sleep_data')
    date = DateField()
    hours = FloatField()
    notes = TextField()

    class Meta:
        database = db

class IsiData(Model):
    id = AutoField()
    user = ForeignKeyField(UserSql, backref='isi_data')
    date_start = DateField()
    date_end = DateField()
    score = IntegerField()

    class Meta:
        database = db

## SQL engine
def create_tables():
    with db:
        db.create_tables([
            UserSql,
            BlackListedJwt,
            Practice,
            PracticeJoinCodes,
            UserToPractice,
            SleepData,
            IsiData
        ])

db.connect()
create_tables()
db.close()
