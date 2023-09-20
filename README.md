
## Usefull Packages

https://github.com/invertase/react-native-firebase/tree/main#readme
https://www.npmjs.com/package/@react-native-firebase/app-check
`npm i -S @react-native-firebase/app-check`

https://github.com/kedros-as/react-native-google-play-integrity
https://www.npmjs.com/package/react-native-google-play-integrity
`npm i -S react-native-google-play-integrity`

https://github.com/bpofficial/expo-attestation#readme
https://www.npmjs.com/package/expo-attestation
`npm i -S expo-attestation`


## Handy Test Commands
```bash
jq --arg content "$(cat fixtures/request_issuance.json | base64)" --arg name "jason" '.content |= $content | .name |= $name' fixtures/basic_message.json
```
```bash
jq --arg content "$(cat fixtures/request_issuance.json | base64)" '.content |= $content' fixtures/basic_message.json|curl -v -X POST -H "Content-Type: application/json" -d @- http://localhost:5000/topic/basicmessages/
```

```bash
jq -s '.[0] * .[1]' source.json target.json
```

```bash
jq --arg content "$(jq -s '.[0] * .[1]' fixtures/chalange_response.json attestation.json | base64)" '.content |= $content' fixtures/basic_message.json| curl -v -X POST -H "Content-Type: application/json" -d @- http://localhost:5000/topic/basicmessages/
```

## Apple Verifications Steps

- [x] Use the decoded object, along with the key identifier that your app sends, to perform the following steps:

- [x] Verify that the x5c array contains the intermediate and leaf certificates for App Attest, starting from the credential certificate in the first data buffer in the array (credcert). Verify the validity of the certificates using Apple’s App Attest root certificate.

- [x] Create clientDataHash as the SHA256 hash of the one-time challenge your server sends to your app before performing the attestation, and append that hash to the end of the authenticator data (authData from the decoded object).

- [x] Generate a new SHA256 hash of the composite item to create nonce.

- [x] Obtain the value of the credCert extension with OID 1.2.840.113635.100.8.2, which is a DER-encoded ASN.1 sequence. Decode the sequence and extract the single octet string that it contains. Verify that the string equals nonce.

- [ ] Create the SHA256 hash of the public key in credCert, and verify that it matches the key identifier from your app.

- [ ] Compute the SHA256 hash of your app’s App ID, and verify that it’s the same as the authenticator data’s RP ID hash.

- [ ] Verify that the authenticator data’s counter field equals 0.

- [ ] Verify that the authenticator data’s aaguid field is either appattestdevelop if operating in the development environment, or appattest followed by seven 0x00 bytes if operating in the production environment.

- [ ] Verify that the authenticator data’s credentialId field is the same as the key identifier.

After successfully completing these steps, you can trust the attestation object.