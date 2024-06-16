from peewee import *

db = PostgresqlDatabase(host='127.0.0.1', user='postgres', port=5432,database='tg-bot-for-bank-db', password='root')

class BaseModel(Model):
    id = PrimaryKeyField(unique=True)
    class Meta:
        database = db

class Positions(BaseModel):
    title = CharField(null=True)

class Employees(BaseModel):
    tg_id = IntegerField()
    position_id = ForeignKeyField(Positions)
    lastname = CharField()
    firstname = CharField()
    patronymic = CharField()


