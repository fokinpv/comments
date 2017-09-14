import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from comments.models import Base
from comments.webapp import create_flask_app


@pytest.fixture
def database_url(tmpdir):
    return f'sqlite:///{tmpdir.join("db.sqlite")}'

@pytest.fixture
def snapshots_dir(tmpdir):
    d = tmpdir.mkdir('snapshots')
    return d


@pytest.fixture
def create_tables(database_url):
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def db_session(monkeypatch, create_tables, database_url):
    engine = create_engine(database_url)
    session = scoped_session(sessionmaker(bind=engine))

    yield session
    session.remove()


@pytest.fixture
def config(database_url, snapshots_dir):
    return {
        'database_url': database_url,
        'snapshots_dir': snapshots_dir,
    }


@pytest.fixture
def webapp(config):
    app = create_flask_app(config)
    return app


@pytest.fixture
def client(webapp):
    with webapp.test_client() as client:
        yield client
