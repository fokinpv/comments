"""Module contains tasks which will be run in Worker.

Each tasks must be independent pieace of code
in order to be run in separate Process.
"""

import logging
from uuid import uuid4
from pathlib import Path

from lxml import etree
from sqlalchemy import and_
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from comments.models import Comment, Snapshot

log = logging.getLogger(__name__)


def create_snapshot(db_url, output_dir, snapshot_id, source,
                    from_datetime=None, to_datetime=None):

    Session = sessionmaker(bind=create_engine(db_url))
    db_session = Session()

    if 'user_id' in source:
        snapshot_type = 'FOR_USER'
    elif ('entity_type_id' in source) and ('entity_id' in source):
        snapshot_type = 'FOR_ENTITY'
    else:
        log.error('Error in creating Snapshot.')

    comments_query = (
        db_session.query(Comment)
    )

    if snapshot_type == 'FOR_USER':
        comments_query = (
            comments_query.filter(Comment.user_id == source['user_id'])
        )
    elif snapshot_type == 'FOR_ENTITY':
        comments_query = (
            comments_query.filter(
                and_(
                    Comment.entity_type_id == source['entity_type_id'],
                    Comment.entity_id == source['entity_id']
                )
            )
        )

    if (from_datetime is not None) and (to_datetime is not None):
        comments_query = (
            comments_query.filter(
                and_(
                    Comment.created_at >= from_datetime,
                    Comment.created_at <= to_datetime,
                )
            )
        )

    comments = comments_query.all()

    root = etree.Element('comments')
    for comment in comments:
        node = etree.SubElement(
            root, 'comment',
            user_id=str(comment.user_id),
            parent_type_id=str(comment.parent_type_id),
            parent_id=str(comment.parent_id),
            created_at=str(comment.created_at),
            updated_at=str(comment.updated_at)
        )
        node.text = comment.text

    filename = f'{uuid4()}.xml'
    output_path = Path(output_dir)
    filepath = output_path / filename

    with open(filepath, 'wb') as xml_file:
        tree = etree.ElementTree(root)
        try:
            tree.write(
                xml_file, pretty_print=True,
                xml_declaration=True,
                encoding='utf-8'
            )
        except Exception as e:
            log.error(e)

    snapshot = (
        db_session.query(Snapshot).get(snapshot_id)
    )
    snapshot.xml_filepath = str(filepath)

    try:
        db_session.commit()
    except Exception as e:
        log.error(e)
