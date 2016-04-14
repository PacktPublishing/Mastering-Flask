import os

from sqlalchemy import event

from flask import Flask
from flask.ext.login import current_user
from flask.ext.principal import identity_loaded, UserNeed, RoleNeed

from .models import db, Reminder, User, Role, Post, Comment, Tag
from .extensions import (
    bcrypt,
    oid,
    login_manager,
    principals,
    rest_api,
    celery,
    debug_toolbar,
    cache,
    assets_env,
    main_js,
    main_css,
    admin,
    mail
)
from .controllers.main import main_blueprint
from .controllers.blog import blog_blueprint
from .controllers.rest.auth import AuthApi
from .controllers.rest.post import PostApi
from .controllers.admin import (
    CustomView,
    CustomModelView,
    CustomFileAdmin,
    PostView
)
from .tasks import on_reminder_save


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
    event.listen(Reminder, 'after_insert', on_reminder_save)

    bcrypt.init_app(app)
    oid.init_app(app)
    login_manager.init_app(app)
    principals.init_app(app)
    celery.init_app(app)
    debug_toolbar.init_app(app)
    cache.init_app(app)
    assets_env.init_app(app)
    admin.init_app(app)
    mail.init_app(app)

    assets_env.register("main_js", main_js)
    assets_env.register("main_css", main_css)

    admin.add_view(CustomView(name='Custom'))
    admin.add_view(
        CustomModelView(
            User, db.session, category='Models'
        )
    )
    admin.add_view(
        CustomModelView(
            Role, db.session, category='Models'
        )
    )
    admin.add_view(
        PostView(
            Post, db.session, category='Models'
        )
    )
    admin.add_view(
        CustomModelView(
            Comment, db.session, category='Models'
        )
    )
    admin.add_view(
        CustomModelView(
            Tag, db.session, category='Models'
        )
    )
    admin.add_view(
        CustomModelView(
            Reminder, db.session, category='Models'
        )
    )
    admin.add_view(
        CustomFileAdmin(
            os.path.join(os.path.dirname(__file__), 'static'),
            '/static/',
            name='Static Files'
        )
    )

    rest_api.add_resource(
        AuthApi,
        '/api/auth'
    )
    rest_api.add_resource(
        PostApi,
        '/api/post',
        '/api/post/<int:post_id>'
    )
    rest_api.init_app(app)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        # Set the identity user object
        identity.user = current_user

        # Add the UserNeed to the identity
        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))

        # Add each role to the identity
        if hasattr(current_user, 'roles'):
            for role in current_user.roles:
                identity.provides.add(RoleNeed(role.name))

    app.register_blueprint(main_blueprint)
    app.register_blueprint(blog_blueprint)

    return app
