from flask import Flask
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from apis.api import (
    healthcheck_blueprint, 
    vessels_blueprint, 
    equipments_blueprint,
    operation_order_blueprint
)

def create_app(app_name='VESSELS', test_config=False, production_conf=False):
    app = Flask(app_name)

    if test_config:
        app.config.from_object('config.TestConfig')
    else:
        app.config.from_object('config.RunConfig')

    from apis.models.model import db, migrate, ma
    migrate = Migrate(app, db)
    ma = Marshmallow(app)

    # Register api blueprints
    app.register_blueprint(healthcheck_blueprint)
    app.register_blueprint(vessels_blueprint, url_prefix='/vessel')
    app.register_blueprint(equipments_blueprint, url_prefix='/equipment')
    app.register_blueprint(operation_order_blueprint, url_prefix='/operation_order')

    db.init_app(app)
    migrate.init_app(app, db)

    return app


if __name__ == "__main__":
   app = create_app(production_conf=False)
   app.run(host="0.0.0.0", port='5000', debug=True)
