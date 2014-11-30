from flask import Flask
from flask.ext.script import Manager
from app.question_module.commands.collect_question import CollectQuestion

app = Flask(__name__)
app.config.from_pyfile("expert_system.cfg", silent=True)

manager = Manager(app)

manager.add_command('collect-question', CollectQuestion())

if __name__ == "__main__":
    manager.run()