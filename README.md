# Comments

[![Build Status](https://travis-ci.org/fokinpv/comments.svg?branch=master)](https://travis-ci.org/fokinpv/comments)
[![codecov](https://codecov.io/gh/fokinpv/comments/branch/master/graph/badge.svg)](https://codecov.io/gh/fokinpv/comments)


Web service for comments

##  Requirements

* Python 3.6+

## Installation

    (env) $ pip install -r requirements.txt
    (env) $ ./cli createdb --config config.yaml
    (env) $ ./cli run --config config.yaml

## Development

    (env) $ pip install -r requirements-dev.txt

Use `pip-tools` to manage dependencies.

### Testing

    (env) $ ./run-tests.sh
