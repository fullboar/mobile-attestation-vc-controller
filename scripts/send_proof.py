import os
import json
import sys

sys.path.insert(0, "./src")

from traction import create_presentation_request, send_presentation_request

connection_id = "0c5a9a9f-939a-4332-a0f2-ee0fd1f68442"

with open(os.path.join("./fixtures/", "request_attest_verif.json"), "r") as f:
    proof_request = json.load(f)

create_presentation_response = create_presentation_request(proof_request)

# print(json.dumps(create_presentation_response, indent=2))

payload = {
    "connection_id": connection_id,
    "presentation_request": {
        **create_presentation_response["by_format"]["pres_request"],
    },
}

# print(json.dumps(payload, indent=2))

send_presentation_response = send_presentation_request(payload)

print(f'Send presentation status = {send_presentation_response["state"]}')
