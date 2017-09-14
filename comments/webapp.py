import sys
import logging

from sqlalchemy import create_engine
from flask import Flask

from .api.users import users
from .api.comments import comments
from .api.snapshots import snapshots
from .database import db_session
from .worker import Worker

log = logging.getLogger(__name__)


def create_flask_app(config):
    app = Flask('comments')

    database_url = config.get('database_url')
    if database_url is None:
        log.error('Database URL not configured')
        sys.exit(1)

    snapshots_dir = config.get('snapshots_dir')

    if snapshots_dir is None:
        log.error('Directory with snapshots not configured')
        sys.exit(1)

    app.worker = Worker(database_url, snapshots_dir)

    engine = create_engine(database_url)
    db_session.configure(bind=engine)

    app.register_blueprint(users)
    app.register_blueprint(comments)
    app.register_blueprint(snapshots)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app
