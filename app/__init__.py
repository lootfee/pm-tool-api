# # from apiflask import APIFlask
# from flask import Flask
# from config import Config
# from pymongo import MongoClient


# class PrefixMiddleware(object):

#     def __init__(self, app, prefix=''):
#         self.app = app
#         self.prefix = prefix

#     def __call__(self, environ, start_response):

#         if environ['PATH_INFO'].startswith(self.prefix):
#             environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
#             environ['SCRIPT_NAME'] = self.prefix
#             return self.app(environ, start_response)
#         else:
#             start_response('404', [('Content-Type', 'text/plain')])
#             return ["This url does not belong to the app.".encode()]
        

# # app = APIFlask(__name__, title='PM Tool API', version='1.0')
# app = Flask(__name__)
# app.debug = True
# app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/api')
# app.config.from_object(Config)
# client = MongoClient('localhost', 27017) # username=app.config['DB_USERNAME'], password=app.config['DB_PASSWORD']
# db = client["pm-tool"]
# PROJECTS = db["projects"]
# TASKS = db["tasks"]
# USERS = db["users"]
# USER_PROJECTS = db["user_projects"]


# from app import users, errors, tokens
from app.create import create_app, ma