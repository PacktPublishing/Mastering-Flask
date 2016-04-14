from gzip import GzipFile
from io import BytesIO

from flask import (
    flash,
    redirect,
    url_for,
    session,
    request
)
from flask.ext.bcrypt import Bcrypt
from flask.ext.openid import OpenID
from flask_oauth import OAuth
from flask.ext.login import LoginManager
from flask.ext.principal import Principal, Permission, RoleNeed
from flask.ext.restful import Api
from flask.ext.celery import Celery
from flask.ext.debugtoolbar import DebugToolbarExtension
from flask.ext.cache import Cache
from flask_assets import Environment, Bundle
from flask.ext.admin import Admin
from flask_mail import Mail

bcrypt = Bcrypt()
oid = OpenID()
oauth = OAuth()
principals = Principal()
rest_api = Api()
celery = Celery()
debug_toolbar = DebugToolbarExtension()
cache = Cache()
assets_env = Environment()
admin = Admin()
mail = Mail()

admin_permission = Permission(RoleNeed('admin'))
poster_permission = Permission(RoleNeed('poster'))
default_permission = Permission(RoleNeed('default'))

login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.session_protection = "strong"
login_manager.login_message = "Please login to access this page"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(userid):
    from models import User
    return User.query.get(userid)


@oid.after_login
def create_or_login(resp):
    from models import db, User
    username = resp.fullname or resp.nickname or resp.email

    if not username:
        flash('Invalid login. Please try again.', 'danger')
        return redirect(url_for('main.login'))

    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User(username)
        db.session.add(user)
        db.session.commit()

    session['username'] = username
    return redirect(url_for('blog.home'))


facebook = oauth.remote_app(
    'facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key='',
    consumer_secret='',
    request_token_params={'scope': 'email'}
)

twitter = oauth.remote_app(
    'twitter',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key='',
    consumer_secret=''
)


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('facebook_oauth_token')


@twitter.tokengetter
def get_twitter_oauth_token():
    return session.get('twitter_oauth_token')


main_css = Bundle(
    'css/bootstrap.css',
    filters='cssmin',
    output='css/common.css'
)

main_js = Bundle(
    'js/jquery.js',
    'js/bootstrap.js',
    filters='jsmin',
    output='js/common.js'
)


class GZip(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.after_request(self.after_request)

    def after_request(self, response):
        encoding = request.headers.get('Accept-Encoding')

        if 'gzip' not in encoding or \
           not response.status_code == 200 or \
           'Content-Encoding' in response.headers:
            return response

        response.direct_passthrough = False

        gzip_buffer = BytesIO()
        with GzipFile(mode='wb', compresslevel=5, fileobj=gzip_buffer) as gzip_file:
            gzip_file.write(response.get_data())

        response.set_data(bytes(gzip_buffer.getvalue()))

        response.headers['Content-Encoding'] = 'gzip'
        response.headers['Content-Length'] = response.content_length

        return response

flask_gzip = GZip()
