from peewee import Model, PrimaryKeyField, PostgresqlDatabase, CharField, IntegerField, ForeignKeyField

from bot.config_reader import config

db = PostgresqlDatabase(
    host=config.host.get_secret_value(),
    user=config.user.get_secret_value(),
    port=config.port.get_secret_value(),
    database=config.database.get_secret_value(),
    password=config.password.get_secret_value()
)


class BaseModel(Model):
    id = PrimaryKeyField(unique=True)

    class Meta:
        database = db


class Positions(BaseModel):
    title = CharField(null=True)


class Employees(BaseModel):
    tg_id = IntegerField()
    tg_username = CharField(null=True)
    position_id = ForeignKeyField(Positions)
    lastname = CharField()
    firstname = CharField()
    patronymic = CharField()
