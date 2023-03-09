import os
import dash
import dash_bootstrap_components as dbc
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
# Uncomment the next line for local use
from dotenv import load_dotenv
from flask_migrate import Migrate
from helpers import yaml_writer
from werkzeug.security import generate_password_hash

external_stylesheets = [dbc.themes.DARKLY]
# Uncomment the next line for local use
load_dotenv()
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


@server.before_first_request
def load_initial_db_data():
    roles = db.session.query(Role).first()
    raid_types = db.session.query(RaidType).first()
    admin = db.session.query(User).first()
    profession = db.session.query(Profession).first()
    build_types = db.session.query(BuildType).first()
    print('****************')
    print('INITIAL DB DATA')
    print('****************')
    db_data = yaml_writer.load_file('initial_db_data.yaml')
    if not roles:
        print('No roles in db')
        for role in db_data['roles']:
            r = Role()
            r.name = role['name']
            r.power = role['power']
            db.session.add(r)
            db.session.commit()
    if not raid_types:
        print('No raid types in db')
        for raid_type in db_data['raid_types']:
            rt = RaidType()
            rt.name = raid_type['name']
            db.session.add(rt)
            db.session.commit()
    if not admin:
        print('No admin in db')
        print(db_data['admin_user'][0])
        user = User(db_data['admin_user'][0]['username'])
        user.password = generate_password_hash(db_data['admin_user'][0]['password'])
        user.role_id = db_data['admin_user'][0]['role_id']
        user.active = db_data['admin_user'][0]['active']
        db.session.add(user)
        db.session.commit()
    if not profession:
        print('No profession in db')
        for profession in db_data['professions']:
            prof = Profession()
            prof.name = profession['name']
            prof.abbreviation = profession['abbreviation']
            prof.color = profession['color'][1:]
            db.session.add(prof)
            db.session.commit()
    if not build_types:
        print('No build types in db')
        for build_type in db_data['build_types']:
            bt = BuildType()
            bt.name = build_type['name']
            db.session.add(bt)
            db.session.commit()
