import base64
import json
import secrets
import time
from flask import Flask, request, make_response, jsonify
from traction import get_connection, send_message, offer_attestation_credential
from apple import verify_attestation_statement

app = Flask(__name__)

def handle_connection(connection_id):
    print("handle_connection")

    connection = get_connection(connection_id)
    if connection['rfc23_state'] != 'completed':
        print("connection is not completed")
        return

    with open('fixtures/request_attestation.json', 'r') as f:
        request_attestation = json.load(f)

    request_attestation['nonce'] = secrets.token_hex(16)
    json_str = json.dumps(request_attestation)
    base64_str = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')

    print(f"sending request attestation message to {connection_id}")

    send_message(connection_id, base64_str)


def handle_message(message, content):
    action = content.get('action')
    handler = {
        'request_issuance': handle_request_issuance_action,
        'challenge_response': handle_challenge_response,
    }.get(action, handle_default)

    return handler(message['connection_id'], content)

def handle_request_issuance_action(connection_id, content):
    print("handle_request_issuance_action")

    return
    # with open('fixtures/request_attestation.json', 'r') as f:
    #     request_attestation = json.load(f)

    # request_attestation['nonce'] = secrets.token_hex(16)
    # json_str = json.dumps(request_attestation)
    # base64_str = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')

    # send_message(connection_id, base64_str)

def handle_challenge_response(connection_id, content):
    print("handle_attestation_chalange")

    platform = content.get('platform')

    if platform == 'apple':
        is_valid_chalange = verify_attestation_statement(content)
        if is_valid_chalange:
            print("chalange is valid")
            offer_attestation_credential(connection_id)
        else:
            print("chalange is invalid")
    else:
        print("unsupported platform")


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
    print("Run POST /topic/basicmessages/")
    message = request.get_json()
    content = message['content']

    if is_base64(content):
        decoded_content = decode_base64_to_json(content)
        if decoded_content['type'] == 'attestation':
            handle_message(message, decoded_content)

    return make_response('', 204)

@app.route('/topic/connections/', methods=['POST'])
def connections():
    print("Run POST /topic/connections/")

    connection = request.get_json()
    print(f"Recieved conneciton = {connection}")
    connectionId = connection['connection_id']

    handle_connection(connectionId)

    return make_response('', 204)

if __name__ == '__main__':
    app.run(debug=True)
