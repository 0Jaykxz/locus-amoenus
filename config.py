from database.database import db
from database.models.tables import *
from routes.user import user_route
from routes.home import home_route

def configure_all(app):
    configure_routes(app)
    configure_db()

def configure_routes(app):
    app.register_blueprint(user_route)
    app.register_blueprint(home_route)

def configure_db():
    db.connect()
    db.create_tables([Escola, Produto, Consumo])
    