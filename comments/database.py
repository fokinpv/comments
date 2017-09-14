from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

db_session = scoped_session(sessionmaker(expire_on_commit=False))

Base = declarative_base()
