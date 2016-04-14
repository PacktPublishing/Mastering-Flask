import os
import datetime
import random

from flask.ext.script import Manager, Server
from flask.ext.script.commands import ShowUrls, Clean
from flask.ext.migrate import Migrate, MigrateCommand

from webapp import create_app
from webapp.models import db, User, Role, Post, Tag, Comment

# default to dev config
env = os.environ.get('WEBAPP_ENV', 'dev')
app = create_app('webapp.config.%sConfig' % env.capitalize())

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command("server", Server())
manager.add_command("show-urls", ShowUrls())
manager.add_command("clean", Clean())
manager.add_command('db', MigrateCommand)


@manager.shell
def make_shell_context():
    return dict(
        app=app,
        db=db,
        User=User,
        Post=Post,
        Tag=Tag,
        Comment=Comment
    )


@manager.command
def setup_db():
    db.create_all()

    admin_role = Role()
    admin_role.name = "admin"
    admin_role.description = "admin"
    db.session.add(admin_role)

    default_role = Role()
    default_role.name = "default"
    default_role.description = "default"
    db.session.add(default_role)

    admin = User()
    admin.username = "admin"
    admin.set_password("password")
    admin.roles.append(admin_role)
    admin.roles.append(default_role)
    db.session.add(admin)

    tag_one = Tag('Python')
    tag_two = Tag('Flask')
    tag_three = Tag('SQLAlechemy')
    tag_four = Tag('Jinja')
    tag_list = [tag_one, tag_two, tag_three, tag_four]

    s = "Body text"

    for i in xrange(100):
        new_post = Post("Post " + str(i))
        new_post.user = admin
        new_post.publish_date = datetime.datetime.now()
        new_post.text = s
        new_post.tags = random.sample(tag_list, random.randint(1, 3))
        db.session.add(new_post)

    db.session.commit()


if __name__ == "__main__":
    manager.run()
