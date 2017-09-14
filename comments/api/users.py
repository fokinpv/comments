from flask import Blueprint

from comments.database import db_session
from comments.models import User, Comment, Snapshot
from comments.schemas import UserSchema, CommentSchema, SnapshotSchema

from . import API_URL
from .utils import json_response

users = Blueprint('users_api', __name__)

users_schema = UserSchema(many=True)
comments_schema = CommentSchema(many=True)
snapshots_schema = SnapshotSchema(many=True)


@users.route(f'{API_URL}/users', methods=['GET'])
def get_users():
    users = db_session.query(User).all()
    serialized = users_schema.dump(users)
    return json_response(serialized.data)


@users.route(f'{API_URL}/users/<user_id>/comments', methods=['GET'])
def get_user_comments(user_id):
    comments = (
        db_session.query(Comment).filter(Comment.user_id == user_id).all()
    )

    serialized = comments_schema.dump(comments)

    return json_response(serialized.data)


@users.route(f'{API_URL}/users/<user_id>/snapshots', methods=['GET'])
def get_user_snapshots(user_id):

    snapshots = (
        db_session.query(Snapshot)
        .filter(Snapshot.user_id == user_id)
        .all()
    )

    serialized = snapshots_schema.dump(snapshots)

    return json_response(serialized.data)
