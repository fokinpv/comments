import os.path
import json
import time

from comments.api import API_URL

from utils import jsonify_response


def test_snapshots(client, db_data):

    cartman = db_data['users']['cartman']
    kyle = db_data['users']['kyle']

    data = {
        'user_id': cartman.id,
        'source': {
            'user_id': kyle.id
        }
    }
    data = json.dumps(data)

    resp = client.post(
        f'{API_URL}/snapshots', data=data,
        content_type='application/json'
    )
    assert resp.status_code == 201

    snapshot_location = resp.headers['Location']

    resp = client.get(snapshot_location)

    data = jsonify_response(resp)
    xml_filepath = data['xml_filepath']

    assert os.path.exists(xml_filepath)

    resp = client.get(f'{API_URL}/users/{cartman.id}/snapshots')
    assert resp.status_code == 200

    data = jsonify_response(resp)
    assert len(data) == 1
