from flask.ext.script import Manager, Server
from main import app

manager = Manager(app)
manager.add_command("server", Server())

@manager.shell
def make_shell_context():
    return dict(app=app)

if __name__ == "__main__":
    manager.run()
