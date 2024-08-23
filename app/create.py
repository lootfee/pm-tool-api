from flask import Flask, redirect, url_for, request
# from alchemical.flask import Alchemical
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_mail import Mail
from apifairy import APIFairy
from config import Config

# db = Alchemical()
ma = Marshmallow()
cors = CORS()
mail = Mail()
apifairy = APIFairy()


def create_app(config_class=Config):
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_class)
    print(flask_app.config['DISABLE_AUTH'])
    # extensions
    # from app import models
    # db.init_app(app)
    ma.init_app(flask_app)
    if flask_app.config['USE_CORS']:  # pragma: no branch
        cors.init_app(flask_app)
    mail.init_app(flask_app)
    apifairy.init_app(flask_app)

    # blueprints
    from app.errors import errors
    flask_app.register_blueprint(errors)
    from app.tokens import tokens
    flask_app.register_blueprint(tokens, url_prefix='/api')
    from app.users import users
    flask_app.register_blueprint(users, url_prefix='/api')
    # from app.posts import posts
    # app.register_blueprint(posts, url_prefix='/api')
    # from app.fake import fake
    # flask_app.register_blueprint(fake)

    # # define the shell context
    # @flask_app.shell_context_processor
    # def shell_context():  # pragma: no cover
    #     ctx = {'db': db}
    #     for attr in dir(models):
    #         model = getattr(models, attr)
    #         if hasattr(model, '__bases__') and \
    #                 db.Model in getattr(model, '__bases__'):
    #             ctx[attr] = model
    #     return ctx

    @flask_app.route('/')
    def index():  # pragma: no cover
        return redirect(url_for('apifairy.docs'))

    @flask_app.after_request
    def after_request(response):
        # Werkzeug sometimes does not flush the request body so we do it here
        request.get_data()
        return response

    return flask_app