from itertools import tee

import pytest
from sqlalchemy import and_

from comments.models import (
    User, Comment, CommentPath, Post, Photo, EntityType
)
from comments.queries import insert_into_tree


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


@pytest.fixture
def create_comment(db_session, entity_types):

    comment_type = entity_types['comment']
    post_type = entity_types['post']
    photo_type = entity_types['photo']

    def _create(user, parent, text):

        if isinstance(parent, Comment):
            parent_type = comment_type
        elif isinstance(parent, Post):
            parent_type = post_type
        elif isinstance(parent, Photo):
            parent_type = photo_type
        else:
            assert False

        comment = Comment(
            user_id=user.id,
            parent_type_id=parent_type.id,
            parent_id=parent.id,
            text=text
        )
        db_session.add(comment)
        db_session.commit()
        return comment

    return _create


@pytest.fixture
def create_comments_path(db_session):

    def _create(*comments):
        """Create comments branch."""

        first_comment = comments[0]
        node_exists = (
            db_session
            .query(CommentPath)
            .filter(
                and_(
                    CommentPath.parent_id == first_comment.id),
                    (CommentPath.child_id == first_comment.id)
                )
        )
        if node_exists.first() is None:
            db_session.execute(
                insert_into_tree,
                {'parent_id': first_comment.id, 'child_id': first_comment.id}
            )
            db_session.commit()

        for parent, child in pairwise(comments):
            db_session.execute(
                insert_into_tree,
                {'parent_id': parent.id, 'child_id': child.id}
            )
            db_session.commit()

    return _create


@pytest.fixture
def users(db_session):
    cartman = User(first_name='Eric', last_name='Cartman')
    kyle = User(first_name='Kyle', last_name='Broflovski')

    db_session.add(cartman)
    db_session.add(kyle)
    db_session.commit()

    return {
        'cartman': cartman,
        'kyle': kyle
    }


@pytest.fixture
def entity_types(db_session):
    comment_type = EntityType(name='COMMENT')
    post_type = EntityType(name='POST')
    photo_type = EntityType(name='PHOTO')

    db_session.add(comment_type)
    db_session.add(post_type)
    db_session.add(photo_type)
    db_session.commit()

    return {
        'comment': comment_type,
        'post': post_type,
        'photo': photo_type,
    }


@pytest.fixture
def comments(db_session, users, entities, entity_types,
             create_comment, create_comments_path):

    cartman = users['cartman']
    kyle = users['kyle']

    comment_type = entity_types['comment']
    post_type = entity_types['post']
    photo_type = entity_types['photo']

    post = entities['post']
    photo = entities['photo']

    comment_1 = create_comment(cartman, post, '1')
    comment_2 = create_comment(kyle, comment_1, '2')
    comment_3 = create_comment(cartman, comment_2, '3')
    comment_4 = create_comment(kyle, comment_2, '4')

    create_comments_path(
        comment_1, comment_2, comment_3
    )
    create_comments_path(comment_2, comment_4)

    return {
        '1': comment_1,
        '2': comment_2,
        '3': comment_3,
        '4': comment_4,
    }


@pytest.fixture
def entities(db_session):

    post = Post()
    photo = Photo()

    db_session.add(post)
    db_session.add(photo)
    db_session.commit()

    return {
        'post': post,
        'photo': photo
    }


@pytest.fixture
def db_data(db_session, users, entity_types, entities, comments):
    return {
        'users': users,
        'entities': entities,
        'entity_types': entity_types,
        'comments': comments
    }
