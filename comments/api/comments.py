import datetime as dt
import math
import logging

from flask import Blueprint, Response, request

from sqlalchemy import and_, not_, func

from comments.database import db_session
from comments.models import Comment, CommentPath, EntityType
from comments.queries import insert_into_tree, select_all_comments
from comments.schemas import CommentSchema

from . import API_URL
from .utils import json_response

log = logging.getLogger(__name__)

comments = Blueprint('comments_api', __name__)

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)


def _all_children_comments(comment_id):
    comments = db_session.execute(
        select_all_comments,
        {'comment_id': comment_id}
    )
    serialized = comments_schema.dump(comments)
    return json_response(serialized.data)


def _comments_with_pagination(entity_type_id, entity_id, limit, offset):

    total_count = (
        db_session.query(func.count(Comment.id))
        .filter(
            and_(
                Comment.parent_type_id == entity_type_id,
                Comment.parent_id == entity_id,
            )
        )
        .scalar()
    )

    comments = (
        db_session.query(Comment)
        .filter(
            and_(
                Comment.parent_type_id == entity_type_id,
                Comment.parent_id == entity_id,
            )
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    serialized = comments_schema.dump(comments)

    headers = {
        'X-Current-Page': math.ceil((int(offset) + 1) / int(limit)),
        'X-Total-Pages': math.ceil(total_count / int(limit)),
    }

    return json_response(
        serialized.data,
        headers=headers
    )


@comments.route(
    f'{API_URL}/<entity_type>/<entity_id>/comments', methods=['GET']
)
def get_entity_comments(entity_type, entity_id):
    """Return level1 comments for an enitity."""

    # TODO Get rid of hardcoded types
    mapping = {
        'comments': 'COMMENT',
        'posts': 'POST',
        'photos': 'PHOTO'
    }

    limit = request.args.get('limit')
    offset = request.args.get('offset')

    type_name = mapping[entity_type]

    entity_type_id = (
       db_session.query(EntityType.id)
       .filter(EntityType.name == type_name).scalar()
    )

    # TODO Refactor this into seperate endpoints
    if type_name == 'COMMENT':
        if (limit is None) and (offset is None):
            return _all_children_comments(entity_id)
        elif (limit is not None) and (offset is not None):
            return _comments_with_pagination(
                entity_type_id, entity_id, limit, offset
            )
        else:
            Response(status=400)
    else:
        if (limit is None) or (offset is None):
            return Response(status=400)

        return _comments_with_pagination(
            entity_type_id, entity_id, limit, offset
        )


@comments.route(f'{API_URL}/comments', methods=['POST'])
def post_comments():
    data = request.get_json()

    user_id = data.get('user_id')
    parent_type_id = data.get('parent_type_id')
    parent_id = data.get('parent_id')
    comment_text = data.get('text')

    parent_type = (
        db_session.query(EntityType)
        .filter(EntityType.id == parent_type_id).one()
    )

    if parent_type is None:
        log.error('No parent_type', parent_type_id)
        return Response(status=404)

    comment = Comment(
        user_id=user_id,
        parent_type_id=parent_type_id,
        parent_id=parent_id,
        text=comment_text
    )

    db_session.add(comment)
    db_session.commit()

    if parent_type.name == 'COMMENT':
        db_session.execute(
            insert_into_tree,
            {'parent_id': parent_id, 'child_id': comment.id}
        )
    else:
        db_session.execute(
            insert_into_tree,
            {'parent_id': comment.id, 'child_id': comment.id}
        )
    db_session.commit()

    serialized = comment_schema.dump(comment)
    location = '/'.join([request.base_url, str(comment.id)])

    return json_response(
        serialized.data,
        headers={'Location': location},
        status_code=201
    )


@comments.route(f'{API_URL}/comments/<comment_id>', methods=['PUT'])
def update_comment(comment_id):

    data = request.get_json()
    updated_text = data['text']

    comment = db_session.query(Comment).get(comment_id)
    comment.updated_at = dt.datetime.utcnow()
    comment.text = updated_text
    db_session.commit()

    serialized = comment_schema.dump(comment)
    return json_response(
        serialized.data,
        status_code=200
    )


@comments.route(f'{API_URL}/comments/<comment_id>', methods=['DELETE'])
def delete_comment(comment_id):

    # Test that comment has at least a child
    children = (
        db_session.query(CommentPath)
        .filter(
            and_(
                CommentPath.parent_id == comment_id,
                not_(CommentPath.child_id == comment_id)
            )
        )
    )

    if children.first() is not None:
        return json_response(
            {'message': 'Comment has descedant'},
            status_code=405
        )

    comment = db_session.query(Comment).get(comment_id)
    db_session.delete(comment)
    db_session.commit()

    return Response(status=204)
