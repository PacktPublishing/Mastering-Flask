import datetime

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mongoengine import MongoEngine
from flask.ext.login import AnonymousUserMixin

from webapp.extensions import bcrypt

available_roles = ('admin', 'poster', 'default')

db = SQLAlchemy()
mongo = MongoEngine()

tags = db.Table(
    'post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

roles = db.Table(
    'role_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    posts = db.relationship('Post', backref='user', lazy='dynamic')
    roles = db.relationship(
        'Role',
        secondary=roles,
        backref=db.backref('users', lazy='dynamic')
    )

    def __init__(self, username):
        self.username = username

        default = Role.query.filter_by(name="default").one()
        self.roles.append(default)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def is_authenticated(self):
        if isinstance(self, AnonymousUserMixin):
            return False
        else:
            return True

    def is_active(self):
        return True

    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False

    def get_id(self):
        return unicode(self.id)


class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Role {}>'.format(self.name)


class Post(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255))
    text = db.Column(db.Text())
    publish_date = db.Column(db.DateTime())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    comments = db.relationship(
        'Comment',
        backref='post',
        lazy='dynamic'
    )
    tags = db.relationship(
        'Tag',
        secondary=tags,
        backref=db.backref('posts', lazy='dynamic')
    )

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<Post '{}'>".format(self.title)


class Comment(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    text = db.Column(db.Text())
    date = db.Column(db.DateTime())
    post_id = db.Column(db.Integer(), db.ForeignKey('post.id'))

    def __repr__(self):
        return "<Comment '{}'>".format(self.text[:15])


class Tag(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255))

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<Tag '{}'>".format(self.title)


#
# Mongo Example Code
#

class Userm(mongo.Document):
    username = mongo.StringField(required=True)
    password = mongo.StringField(required=True)
    roles = mongo.ListField(mongo.StringField(choices=available_roles))

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Commentm(mongo.EmbeddedDocument):
    name = mongo.StringField(required=True)
    text = mongo.StringField(required=True)
    date = mongo.DateTimeField(
        default=datetime.datetime.now()
    )

    def __repr__(self):
        return "<Comment '{}'>".format(self.text[:15])


class Postm(mongo.Document):
    title = mongo.StringField(required=True)
    publish_date = mongo.DateTimeField(
        default=datetime.datetime.now()
    )
    user = mongo.ReferenceField(Userm)
    comments = mongo.ListField(
        mongo.EmbeddedDocumentField(Commentm)
    )
    tags = mongo.ListField(mongo.StringField())

    def __repr__(self):
        return "<Post '{}'>".format(self.title)

    meta = {
        'allow_inheritance': True
    }


class BlogPost(Postm):
    text = mongo.StringField(required=True)

    @property
    def type(self):
        return "blog"


class VideoPost(Postm):
    video_object = mongo.StringField(required=True)

    @property
    def type(self):
        return "video"


class ImagePost(Postm):
    image_url = mongo.StringField(required=True)

    @property
    def type(self):
        return "image"


class QuotePost(Postm):
    quote = mongo.StringField(required=True)
    author = mongo.StringField(required=True)

    @property
    def type(self):
        return "quote"
