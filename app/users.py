from apifairy.decorators import other_responses
from flask import Blueprint, abort, request
from apifairy import authenticate, body, response
from bson import ObjectId
from marshmallow import EXCLUDE

from app.database import Database
from app.models import User
from app.schemas import UserSchema, UpdateUserSchema, EmptySchema
from app.auth import token_auth

users = Blueprint('users', __name__)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
update_user_schema = UpdateUserSchema(partial=True)


@users.route('/users', methods=['POST'])
@body(user_schema)
@response(user_schema, 201)
def new(args):
    """Register a new user"""
    # user = User(**args)
    data = request.get_json()
    users_db = Database('users')
    user = users_db.load_one({"email": data['email']})
    message = ''
    if not user:
        users_db = Database('users')
        users_db.save({"name": data['name'], "email": f'{data['email']}@saskpolytech.ca', 
                            "password": User.set_password(data['password'])})
        message = 'user added'
    else:
        message = 'user not added'
    return {'message': message}



@users.route('/users', methods=['GET'])
# @authenticate(token_auth)
@response(users_schema)
def all():
    """Retrieve all users"""
    users_db = Database('users')
    return users_db.load_all()


@users.route('/users/id/<string:user_id>', methods=['GET'])
# @authenticate(token_auth)
@response(user_schema)
@other_responses({404: 'User not found'})
def get(user_id):
    """Retrieve a user by id"""
    users_db = Database('users')
    return users_db.load_one({'_id': ObjectId(user_id)})


@users.route('/users/email/<email>', methods=['GET'])
# @authenticate(token_auth)
@response(user_schema)
@other_responses({404: 'User not found'})
def get_by_email(email):
    """Retrieve a user by email"""
    users_db = Database('users')
    return users_db.load_one({'email': email}) or abort(404)


@users.route('/me', methods=['GET'])
@authenticate(token_auth)
@response(user_schema)
def me():
    """Retrieve the authenticated user"""
    return token_auth.current_user()


@users.route('/me', methods=['PUT'])
# @authenticate(token_auth)
@body(update_user_schema)
@response(user_schema)
def put(data):
    """Edit user information"""
    user = token_auth.current_user()
    if 'password' in data and ('old_password' not in data or
                               not user.verify_password(data['old_password'])):
        abort(400)
    user.update(data)
    # db.session.commit()
    return user

