#!/usr/bin/env python3
import logging.config

import click
from sqlalchemy import create_engine

from comments.models import Base
from comments.webapp import create_flask_app
from comments.utils import parse_config_file


def config_option_callback(ctx, param, value):
    return parse_config_file(value)


config_option = click.option(
    '--config', default='config.yaml',
    callback=config_option_callback,
    metavar='path/to/file', help='Service config file'
)


@click.group()
def cli():
    pass


@cli.command('createdb')
@config_option
def create_db(config):
    database_url = config['database_url']

    engine = create_engine(database_url)
    Base.metadata.create_all(engine)


@cli.command('run')
@config_option
def run(config):
    logging.config.dictConfig(config.get('logging'))

    app = create_flask_app(config)

    app.run(host=config['flask']['HOST'], port=config['flask']['PORT'])


if __name__ == '__main__':
    cli()
