import os
import dash
import dash_bootstrap_components as dbc
from flask import Flask
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
#from dotenv import load_dotenv
from flask_migrate import Migrate
from helpers import yaml_writer

external_stylesheets = [dbc.themes.DARKLY]
#load_dotenv()
server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
app.title = 'Records of Valhalla'
env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
server.config.from_object(env_config)
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(server)
from models import *
migrate = Migrate(server, db, compare_type=True)

layout_config = yaml_writer.load_config_file(db)

server.config.update(SECRET_KEY=os.getenv('SECRET_KEY'))

# Login manager object will be used to login / logout users
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'


@login_manager.user_loader
def load_user(id):
    return db.session.query(User).filter_by(id = id).first()
