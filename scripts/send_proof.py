import os
import json
import sys

sys.path.insert(0, "./src")

from traction import create_presentation_request, send_presentation_request

connection_id = "0c5a9a9f-939a-4332-a0f2-ee0fd1f68442"

with open(os.path.join("./fixtures/", "request_attest_verif.json"), "r") as f:
    proof_request = json.load(f)

request = create_presentation_request(proof_request)

print(json.dumps(request, indent=2))

payload = {
    "connection_id": connection_id,
    "presentation_request": {
        **request["by_format"]["pres_request"],
    },
}

print(json.dumps(payload, indent=2))

pr_response = send_presentation_request(payload)

print(json.dumps(pr_response, indent=2))
