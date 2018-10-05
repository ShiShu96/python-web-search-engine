from app import create_app
from flask_script import Manager, Shell
from app.config import Config
app = create_app(Config)
manager = Manager(app)

def make_shell_context():
    manager.add_command("shell",Shell(make_context=make_shell_context))
    return dict(app=app)

if __name__ == '__main__':    
    manager.run()
