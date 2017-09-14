import datetime as dt

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey

from .database import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)


class Comment(Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    parent_type_id = Column(Integer, ForeignKey('entity_type.id'))
    parent_id = Column(Integer, nullable=False)

    created_at = Column(
        DateTime(timezone=True), default=dt.datetime.utcnow(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), default=dt.datetime.utcnow(), nullable=False
    )

    text = Column(String)


class CommentPath(Base):

    __tablename__ = 'comment_path'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer)
    child_id = Column(Integer)
    level = Column(Integer)


class Snapshot(Base):

    __tablename__ = 'snapshot'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    created_at = Column(
        DateTime(timezone=True), default=dt.datetime.utcnow(), nullable=False
    )
    xml_filepath = Column(String)


class EntityType(Base):
    __tablename__ = 'entity_type'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


class Post(Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True)


class Photo(Base):
    __tablename__ = 'photo'

    id = Column(Integer, primary_key=True)
