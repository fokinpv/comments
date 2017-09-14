from flask import Blueprint, request, current_app

from comments.database import db_session
from comments.models import Snapshot
from comments.schemas import SnapshotSchema

from . import API_URL
from .utils import json_response

snapshots = Blueprint('snapshots_api', __name__)

snapshot_schema = SnapshotSchema()


@snapshots.route(f'{API_URL}/snapshots', methods=['POST'])
def post_snapshots():
    data = request.get_json()

    user_id = data.get('user_id')
    source = data.get('source')

    from_datetime = data.get('from_datetime')
    to_datetime = data.get('to_datetime')

    snapshot = Snapshot(user_id=user_id)
    db_session.add(snapshot)
    db_session.commit()

    serialized = snapshot_schema.dump(snapshot)
    location = '/'.join([request.base_url, str(snapshot.id)])

    current_app.worker.create_snapshot(
        snapshot.id, source, from_datetime, to_datetime
    )

    return json_response(
        serialized.data,
        headers={'Location': location},
        status_code=201
    )


@snapshots.route(f'{API_URL}/snapshots/<snapshot_id>', methods=['GET'])
def get_snapshot(snapshot_id):
    snapshot = db_session.query(Snapshot).get(snapshot_id)
    serialized = snapshot_schema.dump(snapshot)
    return json_response(serialized.data)
