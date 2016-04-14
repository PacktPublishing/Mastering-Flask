import datetime

from flask import abort
from flask.ext.restful import Resource, fields, marshal_with

from webapp.models import db, User, Post, Tag
from .parsers import (
    post_get_parser,
    post_post_parser,
    post_put_parser,
    post_delete_parser
)
from .fields import HTMLField


nested_tag_fields = {
    'id': fields.Integer(),
    'title': fields.String()
}

post_fields = {
    'id': fields.Integer(),
    'author': fields.String(attribute=lambda x: x.user.username),
    'title': fields.String(),
    'text': HTMLField(),
    'tags': fields.List(fields.Nested(nested_tag_fields)),
    'publish_date': fields.DateTime(dt_format='iso8601')
}


class PostApi(Resource):
    @marshal_with(post_fields)
    def get(self, post_id=None):
        if post_id:
            post = Post.query.get(post_id)
            if not post:
                abort(404)

            return post
        else:
            args = post_get_parser.parse_args()
            page = args['page'] or 1

            if args['user']:
                user = User.query.filter_by(username=args['user']).first()
                if not user:
                    abort(404)

                posts = user.posts.order_by(
                    Post.publish_date.desc()
                ).paginate(page, 30)
            else:
                posts = Post.query.order_by(
                    Post.publish_date.desc()
                ).paginate(page, 30)

            return posts.items

    def post(self, post_id=None):
        if post_id:
            abort(400)
        else:
            args = post_post_parser.parse_args(strict=True)

            user = User.verify_auth_token(args['token'])
            if not user:
                abort(401)

            new_post = Post(args['title'])
            new_post.user = user
            new_post.date = datetime.datetime.now()
            new_post.text = args['text']

            if args['tags']:
                for item in args['tags']:
                    tag = Tag.query.filter_by(title=item).first()

                    # Add the tag if it exists. If not, make a new tag
                    if tag:
                        new_post.tags.append(tag)
                    else:
                        new_tag = Tag(item)
                        new_post.tags.append(new_tag)

            db.session.add(new_post)
            db.session.commit()
            return new_post.id, 201

    def put(self, post_id=None):
        if not post_id:
            abort(400)

        post = Post.query.get(post_id)
        if not post:
            abort(404)

        args = post_put_parser.parse_args(strict=True)
        user = User.verify_auth_token(args['token'])
        if not user:
            abort(401)
        if user != post.user:
            abort(403)

        if args['title']:
            post.title = args['title']

        if args['text']:
            post.text = args['text']

        if args['tags']:
            for item in args['tags']:
                tag = Tag.query.filter_by(title=item).first()

                # Add the tag if it exists. If not, make a new tag
                if tag:
                    post.tags.append(tag)
                else:
                    new_tag = Tag(item)
                    post.tags.append(new_tag)

        db.session.add(post)
        db.session.commit()
        return post.id, 201

    def delete(self, post_id=None):
        if not post_id:
            abort(400)

        post = Post.query.get(post_id)
        if not post:
            abort(404)

        args = post_delete_parser.parse_args(strict=True)
        user = User.verify_auth_token(args['token'])
        if user != post.user:
            abort(401)

        db.session.delete(post)
        db.session.commit()
        return "", 204
