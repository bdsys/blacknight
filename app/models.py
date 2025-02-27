from typing import Annotated
from pydantic import BaseModel
from fastapi import Depends
from peewee import *
from datetime import date

# Data models
class SignupUser(BaseModel):
    username: str
    email: str
    password: str
    user_type: str = 'user'

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None


# SQL models -- peewee
db = SqliteDatabase('database.db')
## Classes

class Practice(Model):
    id = AutoField()
    created = DateTimeField()
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

    class Meta:
        database = db

class UserSql(Model):
    id = AutoField()
    username = CharField(unique=True)
    email = CharField(unique=True)
    full_name = CharField(null=True)
    joined = DateField()
    last_updated = DateField(default=date.today)
    disabled = BooleanField(default=True)
    hashed_password = CharField()
    user_type = CharField(default='user')
    associated_practice = ForeignKeyField(Practice, backref='users', null=True)

    class Meta:
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
    date = DateField()
    score = IntegerField()

    class Meta:
        database = db

## SQL engine
db.connect()
db.create_tables([UserSql])
db.create_tables([BlackListedJwt])
db.create_tables([Practice])
db.create_tables([SleepData])
db.create_tables([IsiData])
db.close()
