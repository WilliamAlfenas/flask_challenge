from flask_migrate import MigrateCommand
from flasgger import Swagger
from flask_script import Manager

from apis.app import create_app

app = create_app()
manager = Manager(app)
swagger = Swagger(app)


manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
        