import pytest

from comments.api import API_URL

from utils import jsonify_response

pytest_plugins = ['data_fixture']


def test_get_users(db_session, client, db_data):
    resp = client.get(f'{API_URL}/users')
    assert resp.status_code == 200

    data = jsonify_response(resp)
    assert len(data) == 2


def test_get_user_comments(db_session, client, db_data):
    cartman = db_data['users']['cartman']

    resp = client.get(f'{API_URL}/users/{cartman.id}/comments')
    assert resp.status_code == 200

    data = jsonify_response(resp)
    assert len(data) == 2
