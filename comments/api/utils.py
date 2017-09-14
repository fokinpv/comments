from flask import jsonify


def json_response(data: dict, headers=None, status_code=200):
    resp = jsonify(data)
    resp.status_code = status_code

    if headers is not None:
        for key, val in headers.items():
            resp.headers.set(key, val)

    return resp
