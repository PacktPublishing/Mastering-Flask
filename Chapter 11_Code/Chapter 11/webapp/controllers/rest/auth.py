from flask import abort, current_app
from flask.ext.restful import Resource

from webapp.models import User
from .parsers import user_post_parser

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class AuthApi(Resource):
    def post(self):
        args = user_post_parser.parse_args()
        user = User.query.filter_by(username=args['username']).one()

        if user.check_password(args['password']):
            s = Serializer(current_app.config['SECRET_KEY'], expires_in=604800)
            return {"token": s.dumps({'id': user.id})}
        else:
            abort(401)
