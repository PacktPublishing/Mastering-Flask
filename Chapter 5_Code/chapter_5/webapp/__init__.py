from flask import Flask

from models import db
from controllers.main import main_blueprint
from controllers.blog import blog_blueprint


def create_app(object_name):
    """
    An flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/

    Arguments:
        object_name: the python path of the config object,
                     e.g. project.config.ProdConfig
    """

    app = Flask(__name__)
    app.config.from_object(object_name)

    db.init_app(app)

    app.register_blueprint(main_blueprint)
    app.register_blueprint(blog_blueprint)

    return app

if __name__ == '__main__':
    app = app = create_app('project.config.ProdConfig')
    app.run()
