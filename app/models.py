from flask import current_app, url_for
from app.database import Database
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

import jwt
import uuid
from datetime import datetime, timedelta, timezone
from hashlib import md5
import secrets
from time import time
from typing import Optional


class Token:
    def __init__(self, id):
        tokens_db = Database("tokens")
        u = tokens_db.load_one({"_id": ObjectId(id)})
        self.id = id
        self.access_token = u["access_token"]
        self.access_expiration = u["access_expiration"]
        self.refresh_token = u["refresh_token"]
        self.refresh_expiration = u["refresh_expiration"]
        self.user_id = u["user_id"]

    @property
    def access_token_jwt(self):
        return jwt.encode({'token': self.access_token},
                          current_app.config['SECRET_KEY'],
                          algorithm='HS256')

    def generate(self):
        self.access_token = secrets.token_urlsafe()
        self.access_expiration = datetime.now(timezone.utc) + \
            timedelta(minutes=current_app.config['ACCESS_TOKEN_MINUTES'])
        self.refresh_token = secrets.token_urlsafe()
        self.refresh_expiration = datetime.now(timezone.utc) + \
            timedelta(days=current_app.config['REFRESH_TOKEN_DAYS'])

    def expire(self, delay=None):
        if delay is None:  # pragma: no branch
            # 5 second delay to allow simultaneous requests
            delay = 5 if not current_app.testing else 0
        self.access_expiration = datetime.now(timezone.utc) + timedelta(seconds=delay)
        self.refresh_expiration = datetime.now(timezone.utc) + timedelta(seconds=delay)

    @staticmethod
    def clean():
        """Remove any tokens that have been expired for more than a day."""
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        query = {"refresh_expiration": {"$lt": yesterday}}
        tokens_db = Database("tokens")
        tokens_db.delete_many(query)

    @staticmethod
    def from_jwt(access_token_jwt):
        access_token = None
        try:
            access_token = jwt.decode(access_token_jwt,
                                      current_app.config['SECRET_KEY'],
                                      algorithms=['HS256'])['token']
            tokens_db = Database("tokens")
            return tokens_db.load_one({'access_token': access_token})
        except jwt.PyJWTError:
            pass


class User:
    print('model')
    def __init__(self, name: str, email: str, password: str, id: str = None):
        self.id = id or uuid.uuid4().hex
        self.name = name
        self.email = email
        self.password = password

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.id
    
    @staticmethod
    def set_password(password):
        return generate_password_hash(password)

    @staticmethod
    def check_password(password_hash, password):
        return check_password_hash(password_hash, password)
    
    def generate_auth_token(self):
        token = Token(user=self)
        token.generate()
        return token

    @staticmethod
    def verify_access_token(access_token_jwt, refresh_token=None):
        token = Token.from_jwt(access_token_jwt)
        if token:
            if token.access_expiration > datetime.now(timezone.utc):
                return token.user

    @staticmethod
    def verify_refresh_token(refresh_token, access_token_jwt):
        token = Token.from_jwt(access_token_jwt)
        if token and token.refresh_token == refresh_token:
            if token.refresh_expiration > datetime.now(timezone.utc):
                return token

            # someone tried to refresh with an expired token
            # revoke all tokens from this user as a precaution
            token.user.revoke_all()

    def revoke_all(self):
        tokens_db = Database("tokens")
        tokens_db.delete_one({'user_id': self.id})

    def generate_reset_token(self):
        return jwt.encode(
            {
                'exp': time() + current_app.config['RESET_TOKEN_MINUTES'] * 60,
                'reset_email': self.email,
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_reset_token(reset_token):
        users_db = Database("users")
        try:
            data = jwt.decode(reset_token, current_app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except jwt.PyJWTError:
            return
        return users_db.load_one({'email': data['reset_email']})