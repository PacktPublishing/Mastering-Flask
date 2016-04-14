from webapp import create_app
from webapp.models import db, User, Role

app = create_app('webapp.config.TestConfig')

db.app = app
db.create_all()

default = Role("default")
poster = Role("poster")
db.session.add(default)
db.session.add(poster)
db.session.commit()

test_user = User("test")
test_user.set_password("test")
test_user.roles.append(poster)
db.session.add(test_user)
db.session.commit()

app.run()
