import os

import dash
import dash_bootstrap_components as dbc
from flask import Flask
from flask_login import LoginManager, UserMixin
#from dotenv import load_dotenv

external_stylesheets = [dbc.themes.DARKLY]

server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
server.config.from_object(env_config)

# server = app.server

#load_dotenv()
server.config.update(SECRET_KEY=os.getenv('SECRET_KEY'))

# Login manager object will be used to login / logout users
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'


class User(UserMixin):
    def __init__(self, username):
        self.id = username


@login_manager.user_loader
def load_user(username):
    return User(username)
