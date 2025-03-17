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
    start_date: date
    # end_date: date
    score: int

class GetIsiData(BaseModel):
    start_date: date

class CreateSleepDiaryData(BaseModel):
    entry_date: date
    hours_slept: float
    bedtime_start: date
    bedtime_end: date
    notes: str
    minutes_when_out_of_bed_after_waking: int
    time_to_fall_asleep: date
    number_of_awakenings: int
    time_awake_during_night: date
    final_awakening_time: date
    wake_earlier_than_desried: bool
    minutes_awake_earlier_than_desired: int
    sleep_rating: Literal['very_poor', 'poor', 'fair', 'good', 'very_good']
    notes = TextField()

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
    user_type = CharField(choices=[('user'), ('practitioner')], default='user')

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
    # join_code_1 = CharField(unique=True)
    # join_code_2 = CharField(unique=True)
    # join_code_3 = CharField(unique=True)
    # join_code_4 = CharField(unique=True)
    # join_code_5 = CharField(unique=True)
    join_code_1 = IntegerField()
    join_code_2 = IntegerField()
    join_code_3 = IntegerField()
    join_code_4 = IntegerField()
    join_code_5 = IntegerField()
    created = DateTimeField()

    class Meta:
        database = db

class UserToPractice(Model):
    id = AutoField()
    user = ForeignKeyField(UserSql)
    practice = ForeignKeyField(Practice)
    created = DateTimeField()
    association_type = CharField(choices=[('owner'), ('member'), ('provider')], default='member')

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
    # date_end = DateField() # Removing for now as it seems difficult to use
    score = IntegerField()
    last_updated_by = ForeignKeyField(UserSql, backref='isi_data_updated')
    last_updated = DateTimeField()
    associated_practice = ForeignKeyField(Practice, backref='isi_data', null=True)

    class Meta:
        database = db

class SleepDiaryData(Model):
    id = AutoField()
    user = ForeignKeyField(UserSql, backref='sleep_diary_data')
    last_updated_by = ForeignKeyField(UserSql, backref='isi_data_updated')
    last_updated = DateTimeField()
    associated_practice = ForeignKeyField(Practice, backref='isi_data', null=True)
    entry_date = DateTimeField()
    hours_slept = FloatField()
    bedtime_start = DateTimeField()
    bedtime_end = DateTimeField()
    minutes_when_out_of_bed_after_waking = IntegerField()
    time_to_fall_asleep = DateTimeField()
    number_of_awakenings = IntegerField()
    time_awake_during_night = DateTimeField()
    final_awakening_time = DateTimeField()
    wake_earlier_than_desried = BooleanField()
    minutes_awake_earlier_than_desired = IntegerField()
    sleep_rating = CharField(choices=[('very_poor'), ('poor'), ('fair'), ('good'), ('very_good')])
    notes = TextField()

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
            IsiData,
            SleepDiaryData,
        ])

db.connect()
create_tables()
db.close()
