import json

def jsonify_response(response):
    return json.loads(
        response.data.decode()
    )
