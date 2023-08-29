from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
from pyasn1.codec.der import decoder
from pyasn1.type import univ
from typing import List, Dict, Union
import cbor
import base64
import hashlib

from cryptography.exceptions import InvalidSignature

AppleAppAttestStatement = Dict[str, Union[str, Dict[str, List[bytes]], bytes]]


def decode_apple_attestation_object(object_as_base64: str) -> Union[AppleAppAttestStatement, None]:
    try:
        binary_data = base64.b64decode(object_as_base64)
        return cbor.loads(binary_data)

    except Exception as e:
        # Throws on invalid input
        print(e)

    return None


def create_authdata_with_nonce_hash(attestation_object):
    one_time_challenge = 'My String to Convert into Data'
    hash = hashlib.sha256(one_time_challenge.encode('utf-8')).digest()
    client_data_hash = hash
    concatenated_buffer = attestation_object['authData'] + client_data_hash

    return concatenated_buffer


def create_composite_nonce(concatenated_buffer):
    sha256_hash = hashlib.sha256(concatenated_buffer).hexdigest()

    return sha256_hash


def verify_apple_attestation_object(attestation_object, apple_app_attestation_root_ca_as_base64):
    try:
        root_certificate = x509.load_pem_x509_certificate(base64.b64decode(apple_app_attestation_root_ca_as_base64), default_backend())
        credential_certificate = x509.load_der_x509_certificate(attestation_object['attStmt']['x5c'][0], default_backend())
        intermediate_certificate = x509.load_der_x509_certificate(attestation_object['attStmt']['x5c'][1], default_backend())

        print('root_certificate', root_certificate.subject)
        print('credential_certificate', credential_certificate.subject)
        print('intermediate_certificate', intermediate_certificate.subject)

        if intermediate_certificate.issuer == root_certificate.subject:
            print('The child certificate was issued by the parent certificate.')
        else:
            print('The child certificate was not issued by the parent certificate.')

        # Verify the signature of the certificate using the public key of the root certificate

        assert isinstance(root_certificate.public_key(), ec.EllipticCurvePublicKey)

        if credential_certificate.signature_algorithm_oid not in [
            x509.SignatureAlgorithmOID.ECDSA_WITH_SHA256
        ]:
            return False

        intermediate_certificate_is_valid = root_certificate.public_key().verify(
            intermediate_certificate.signature,
            intermediate_certificate.tbs_certificate_bytes,
            ec.ECDSA(intermediate_certificate.signature_hash_algorithm)
        )

        credential_certificate_is_valid = intermediate_certificate.public_key().verify(
            credential_certificate.signature,
            credential_certificate.tbs_certificate_bytes,
            ec.ECDSA(credential_certificate.signature_hash_algorithm),
        )

        if intermediate_certificate_is_valid is None and credential_certificate_is_valid is None:
            print('The certificates are signed by the ROOT certificate.')

    except InvalidSignature as e:
        print("The certificates are NOT signed by the ROOT certificate.")
        print(e)


def extract_attestation_object_extension(attestation_object, oid='1.2.840.113635.100.8.2'):
    # Load the certificate from a file
    credential_certificate = x509.load_der_x509_certificate(attestation_object['attStmt']['x5c'][0])

    # Get the extension with OID 1.2.840.113635.100.8.2
    cred_cert_extension = credential_certificate.extensions.get_extension_for_oid(x509.ObjectIdentifier(oid))

    # Get the value of the extension
    cred_cert_extension_value = cred_cert_extension.value.value
    decoded_data, _ = decoder.decode(cred_cert_extension_value, asn1Spec=univ.Sequence())

    return decoded_data[0].asOctets().hex()


def create_hash_from_pub_key(cred_certificate):
    certificate = x509.load_der_x509_certificate(cred_certificate)

    # Get the public key from the certificate
    public_key = certificate.public_key()

    # Serialize the public key to bytes
    public_key_bytes = public_key.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)

    # Compute the SHA-256 hash of the public key bytes
    hash_object = hashlib.sha256(public_key_bytes)
    hash_bytes = hash_object.digest()
    hash_hex = hash_bytes.hex()

    # Print the hash as a hexadecimal string
    return hash_hex


def main():
    key_identifier = 'agwlhZx07ky4CBMYYEZgBTBqNUoeBbNDPfKvQ4sIPxc='
    apple_app_attestation_root_ca_as_base64 = 'LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUNJVENDQWFlZ0F3SUJBZ0lRQy9PK0R2SE4wdUQ3akc1eUgySVhtREFLQmdncWhrak9QUVFEQXpCU01TWXcKSkFZRFZRUUREQjFCY0hCc1pTQkJjSEFnUVhSMFpYTjBZWFJwYjI0Z1VtOXZkQ0JEUVRFVE1CRUdBMVVFQ2d3SwpRWEJ3YkdVZ1NXNWpMakVUTUJFR0ExVUVDQXdLUTJGc2FXWnZjbTVwWVRBZUZ3MHlNREF6TVRneE9ETXlOVE5hCkZ3MDBOVEF6TVRVd01EQXdNREJhTUZJeEpqQWtCZ05WQkFNTUhVRndjR3hsSUVGd2NDQkJkSFJsYzNSaGRHbHYKYmlCU2IyOTBJRU5CTVJNd0VRWURWUVFLREFwQmNIQnNaU0JKYm1NdU1STXdFUVlEVlFRSURBcERZV3hwWm05eQpibWxoTUhZd0VBWUhLb1pJemowQ0FRWUZLNEVFQUNJRFlnQUVSVEhobUxXMDdBVGFGUUlFVndUdFQ0ZHljdGRoCk5iSmhGcy9JaTJGZENnQUhHYnBwaFkzK2Q4cWp1RG5nSU4zV1ZoUVVCSEFvTWVRL2NMaVAxc09VdGdqcUs5YXUKWWVuMW1NRXZScTlTazNKbTVYOFU2MkgreFREM0ZFOVRnUzQxbzBJd1FEQVBCZ05WSFJNQkFmOEVCVEFEQVFILwpNQjBHQTFVZERnUVdCQlNza1JCVE03MithRUgvcHd5cDVmcnE1ZVdLb1RBT0JnTlZIUThCQWY4RUJBTUNBUVl3CkNnWUlLb1pJemowRUF3TURhQUF3WlFJd1FnRkduQnl2c2lWYnBUS3dTZ2Ewa1AwZThFZURTNCtzUW1UdmI3dm4KNTNPNStGUlhnZUxocEowNnlzQzVQck95QWpFQXA1VTR4RGdFZ2xsRjdFbjNWY0UzaWV4Wlp0S2VZbnBxdGlqVgpveUZyYVdWSXlkL2RnYW5tcmR1QzFibVRCR3dECi0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0='
    base64_encoded_string = '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'

    # Run the async function in the event loop
    apple_attestation_object = decode_apple_attestation_object(base64_encoded_string)
    if not apple_attestation_object:
        return

    # 1. Verify that the x5c array contains the intermediate and leaf
    # certificates for App Attest, starting from the credential certificate in the first
    # data buffer in the array (credcert). Verify the validity of the certificates using
    # Apple’s App Attest root certificate.

    verify_apple_attestation_object(apple_attestation_object, apple_app_attestation_root_ca_as_base64)

    # 2. Create clientDataHash as the SHA256 hash of the one-time challenge your server sends
    # to your app before performing the attestation, and append that hash to the end of the
    # authenticator data (authData from the decoded object).

    authdata_with_nonce_hash = create_authdata_with_nonce_hash(apple_attestation_object)

    # 3. Generate a new SHA256 hash of the composite item to create nonce.

    composite_nonce = create_composite_nonce(authdata_with_nonce_hash)

    # 4. Obtain the value of the credCert extension with OID 1.2.840.113635.100.8.2,
    # which is a DER-encoded ASN.1 sequence. Decode the sequence and extract the single
    # octet string that it contains. Verify that the string equals nonce.

    extension_value = extract_attestation_object_extension(apple_attestation_object)
    print('nonce match =', extension_value == composite_nonce)

    # 5. Create the SHA256 hash of the public key in credCert, and verify that it matches the
    # key identifier from your app.

    hash = create_hash_from_pub_key(apple_attestation_object['attStmt']['x5c'][0])
    print(hash)

    # Decode the Base64-encoded value to bytes
    bytes_value = base64.b64decode(key_identifier)

    # Compute the SHA-256 hash of the bytes
    hash_object = hashlib.sha256(bytes_value)
    hash_bytes = hash_object.digest()
    hash_hex = hash_bytes.hex()

    # Print the hash as a hexadecimal string
    hash_hex = hash_bytes.hex()
    print(hash_hex)

    print('pub key match =', hash == hash_hex)


if __name__ == "__main__":
    main()

    # 6. Compute the SHA256 hash of your app’s App ID, and verify that it’s the same as the
    # authenticator data’s RP ID hash.
    # 7. Verify that the authenticator data’s counter field equals 0.
    # 8. Verify that the authenticator data’s aaguid field is either appattestdevelop if
    # operating in the development environment, or appattest followed by seven 0x00
    # bytes if operating in the production environment.
    # 9. Verify that the authenticator data’s credentialId field is the same as the
    # key identifier.
