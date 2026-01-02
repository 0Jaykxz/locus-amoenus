from peewee import *
from database.database import db

class BaseModel(Model):
    class Meta:
        database = db

class Escola(BaseModel):
    nome = CharField(unique=True)

class Produto(BaseModel):
    nome = CharField(unique=True)

class Consumo(BaseModel):
    data = DateField()
    escola = ForeignKeyField(Escola, backref='consumos')
    produto = ForeignKeyField(Produto, backref='consumos')
    quantidade = IntegerField()
    unidade = CharField(choices=[('UN', 'Unidade'), ('CX', 'Caixa'),  ('PC', 'Pacote')])
