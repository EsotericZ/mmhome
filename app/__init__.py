from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from flask import session
from flask_socketio import SocketIO, emit
from flask_login import current_user, logout_user

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@socketio.on('disconnect')
def disconnect_user():
    logout_user()
    session.pop('yourkey', None)

from app import routes, models
