import datetime
from os import environ
from flask_cors import CORS
from config_parser import config_parser
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from logger import app_logger

from accesscontrol import roles_required, AllowedRoles
from models.user import UserModel
from resources.company import CompanyResource, CompaniesResource, CompanyRegister
from resources.program import ProgramResource, ProgramRegister, ProgramsResource
from resources.user import UserResource, User, UserLogin, UserLogout, RefreshToken, Users
from resources.register import RegisterResource
from google_drive import GoogleDriveCommands
from helpers import to_json
from resources.week import WeekResource, WeekRegister, WeeksResource

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=5)

db_local_prefix = config_parser.get('Database', 'local_prefix')
db_remote_prefix = config_parser.get('Database', 'remote_prefix')
local_db_name = f"{db_local_prefix}{config_parser.get('Database', 'url')}"
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL', local_db_name)
app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace(db_remote_prefix, db_local_prefix)

app.secret_key = f"{config_parser.get('Common', 'secret_key')}"


api = Api(app)
CORS(app)

jwt = JWTManager(app)


@jwt.additional_claims_loader
def add_role_claims_to_access_token(identity):
    user = UserModel.find_by_id(identity)
    if user:
        return {'role': user.role.json()}


@jwt.token_in_blocklist_loader
def token_in_blocklist_callback(_, jwt_payload: dict):
    return jwt_payload['jti'] in UserLogout.BLACKLIST


api.add_resource(UserResource, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(Users, '/users')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(RefreshToken, '/refresh')

api.add_resource(CompanyResource, '/company/<int:company_id>')
api.add_resource(CompanyRegister, '/company')
api.add_resource(CompaniesResource, '/company/all')

api.add_resource(ProgramResource, '/program/<int:program_id>')
api.add_resource(ProgramRegister, '/program')
api.add_resource(ProgramsResource, '/program/all')

api.add_resource(WeekResource, '/week/<int:week_id>')
api.add_resource(WeekRegister, '/week')
api.add_resource(WeeksResource, '/week/all')


api.add_resource(RegisterResource, '/create_school_register/<int:program_id>')


@app.route("/")
@roles_required([AllowedRoles.admin.name, AllowedRoles.program_manager.name])
def main_page():
    return {'message': "You've entered home page"}, 200


@app.route("/remote_folders_list")
@roles_required([AllowedRoles.admin.name, AllowedRoles.program_manager.name])
def remote_folders_list():
    res = to_json(GoogleDriveCommands.search())
    return {'remote_folders': res}, 200


@app.route("/show_logs")
@roles_required([AllowedRoles.admin.name])
def show_logs():
    log_res = ""
    with open("rykosystem.log", 'r+') as log_file:
        log_res = log_file.read()
        if log_res:
            app_logger.info(f"{log_res}")
            log_file.truncate(0)
        else:
            return {'message': 'Log file empty'}, 200
    return {'message': f'Log file data: {log_res}'}, 200


if __name__ == '__main__':
    from db import db


    @app.before_first_request
    def create_tables():
        db.create_all()

    db.init_app(app)
    app.run(debug=True, host="0.0.0.0")
