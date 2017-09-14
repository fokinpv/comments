import json

import pytest

from comments.api import API_URL
from comments.models import Comment, Post

from utils import jsonify_response

pytest_plugins = ['data_fixture']


@pytest.fixture(autouse=True)
def monkeypatch_dbsession(monkeypatch, db_session):
    monkeypatch.setattr('comments.api.comments.db_session', db_session)


def test_post_comment_to_entity(db_session, client, db_data):

    comment_data = {
        'user_id': 1,
        'parent_type_id': 2,
        'parent_id': 1,
        'text': 'Hello, World!'
    }
    data_json = json.dumps(comment_data)

    resp = client.post(
        f'{API_URL}/comments', data=data_json,
        content_type='application/json'
    )
    assert resp.status_code == 201
    assert resp.headers['Location']

    data = jsonify_response(resp)


def test_post_comment_to_comment(db_session, client, db_data):

    comment_data = {
        'user_id': 1,
        'parent_type_id': 2,
        'parent_id': 1,
        'text': 'CommentToPost'
    }
    data_json = json.dumps(comment_data)

    resp = client.post(
        f'{API_URL}/comments', data=data_json,
        content_type='application/json'
    )
    assert resp.status_code == 201

    comment_data = {
        'user_id': 1,
        'parent_type_id': 1,
        'parent_id': 1,
        'text': 'CommentToComment'
    }
    data_json = json.dumps(comment_data)

    resp = client.post(
        f'{API_URL}/comments', data=data_json,
        content_type='application/json'
    )
    assert resp.status_code == 201

    data = jsonify_response(resp)
    assert data['user_id'] == 1

def test_get_comments(db_session, client, db_data):

    comment = db_data['comments']['1']

    resp = client.get(
        f'{API_URL}/comments/{comment.id}/comments',
        content_type='application/json'
    )
    assert resp.status_code == 200

    data = jsonify_response(resp)
    assert len(data) == 4


def test_update_comment(db_session, client, db_data):
    comment = db_data['comments']['1']

    old_udpdate_at = comment.updated_at

    data = {
        'text': 'updated comment'
    }
    data_json = json.dumps(data)

    resp = client.put(
        f'{API_URL}/comments/{comment.id}',
        data=data_json,
        content_type='application/json'
    )
    assert resp.status_code == 200

    updated_comment = db_session.query(Comment).get(comment.id)
    new_udpdate_at = updated_comment.updated_at

    assert updated_comment.text == 'updated comment'
    assert old_udpdate_at < new_udpdate_at


def test_delete_comment_fail(db_session, client, db_data):
    comment = db_data['comments']['1']

    resp = client.delete(
        f'{API_URL}/comments/{comment.id}',
        content_type='application/json'
    )
    assert resp.status_code == 405

    data = jsonify_response(resp)
    assert data['message'] != ''

    comment = db_session.query(Comment).get(comment.id)
    assert comment is not None


def test_delete_comment_success(db_session, client, db_data):

    comment = db_data['comments']['4']

    resp = client.delete(
        f'{API_URL}/comments/{comment.id}',
        content_type='application/json'
    )
    assert resp.status_code == 204

    comment = db_session.query(Comment).get(comment.id)
    assert comment is None


def test_get_entity_comments(db_session, client, db_data, create_comment):

    post = Post()
    db_session.add(post)
    db_session.commit()

    kyle = db_data['users']['kyle']

    comments = []
    for i in range(6):
        comment = create_comment(kyle, post, 'Hi ' + str(i))
        comments.append(comment)

    resp = client.get(f'{API_URL}/posts/{post.id}/comments?limit=5&offset=0')
    assert resp.status_code == 200

    assert resp.headers['X-Current-Page'] == '1'
    assert resp.headers['X-Total-Pages'] == '2'

    data = jsonify_response(resp)
    assert len(data) == 5

    resp = client.get(f'{API_URL}/posts/{post.id}/comments?limit=5&offset=5')
    assert resp.status_code == 200

    assert resp.headers['X-Current-Page'] == '2'
    assert resp.headers['X-Total-Pages'] == '2'

    data = jsonify_response(resp)
    assert len(data) == 1

    last_comment = comments[-1]

    assert data[0]['id'] == last_comment.id
