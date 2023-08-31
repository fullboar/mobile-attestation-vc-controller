from flask import Flask, request, make_response, jsonify
import base64
import json
from traction import send_message

app = Flask(__name__)

def handle_message(message, content):
    action = content.get('action')
    handler = {
        'request_issuance': handle_request_issuance_action,
        'attestation_chalange': handle_attestation_chalange,
    }.get(action, handle_default)

    return handler(message['connection_id'], content)

def handle_request_issuance_action(connection_id, content):
    print("handle_request_issuance_action")

    with open('fixtures/request_attestation.json', 'r') as f:
        request_attestation = json.load(f)

    request_attestation['nonce'] = "1234567890"
    json_str = json.dumps(request_attestation)
    base64_str = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')

    send_message(connection_id, base64_str)

def handle_attestation_chalange(connection_id, content):
    print("handle_attestation_chalange")

def handle_default(connection_id, content):
    # Handle default case
    pass

def is_base64(s):
    try:
        # Attempt to decode the string as base64
        base64.b64decode(s)
        return True
    except Exception:
        # If an exception is raised, the string is not base64 encoded
        return False

def decode_base64_to_json(s):
    decoded = base64.b64decode(s)
    json_str = decoded.decode('utf-8')
    json_obj = json.loads(json_str)

    return json_obj

@app.route('/topic/basicmessages/', methods=['POST'])
def basicmessages():
    message = request.get_json()
    content = message['content']

    if is_base64(content):
        decoded_content = decode_base64_to_json(content)
        if decoded_content['type'] == 'attestation':
            handle_message(message, decoded_content)

    return make_response('', 204)


if __name__ == '__main__':
    app.run(debug=True)
