from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
from dotenv import load_dotenv

load_dotenv()
path = os.getenv("GOOGLE_AUTH_JSON_PATH")
creds = service_account.Credentials.from_service_account_file(
    path, scopes=['https://www.googleapis.com/auth/playintegrity']
)

# should eventually confirm nonce matches here
def isValidVerdict(verdict):
    try:
        valid_device_verdicts = ['MEETS_DEVICE_INTEGRITY']
        # nonce = verdict['tokenPayloadExternal']['requestDetails']['nonce']
        request_package_name = verdict['tokenPayloadExternal']['requestDetails']['requestPackageName']
        package_name = verdict['tokenPayloadExternal']['appIntegrity']['packageName']
        # app_verdict = verdict['tokenPayloadExternal']['appIntegrity']['appRecognitionVerdict']
        device_verdicts = verdict['tokenPayloadExternal']['deviceIntegrity']['deviceRecognitionVerdict']
        if (
                request_package_name == 'ca.bc.gov.BCWallet' and
                package_name == 'ca.bc.gov.BCWallet' and
                # app_verdict == 'PLAY_RECOGNIZED' and
                set(valid_device_verdicts).issubset(device_verdicts)
        ):
            return True
        else:
            return False
    except Exception as e:
        print('Error evaluating verdict:', e)
        return False


# decrypt the integrity token on google's servers
def verify_integrity_token(token):
    try:
        service = build('playintegrity', 'v1', credentials=creds)
        body = {
            "integrityToken": token
        }
        instance = service.v1()
        verdict = instance.decodeIntegrityToken(packageName='ca.bc.gov.BCWallet', body=body).execute()
        if (isValidVerdict(verdict)):
            return True
        else:
            return False
    except Exception as e:
        print('Error verifying integrity token:', e)
        return False
    else:
        return False


def main():
    print('testing google decryption and validation')
    # test token
    # tokenStr = "eyJhbGciOiJBMjU2S1ciLCJlbmMiOiJBMjU2R0NNIn0.KFblol_9JhOlET2f9elkRQikcIT9es3um64ZnvuAREYfJNvWYVlkVA.cxjbb-d8n6JBCCE5.9OXiSYrz7_PIRGGzwUMO0M_Fp66gPwYphTsJwY1eF-vYnKGTnHtxxIIuriNAHBxPBtyzauEVC4eNkz-wQwoRUx7WjpMpIqDpLRpIDFJ4D0cbbsEiqoSMHY3ik5xIWWuZfj84tL8AJ_Eq28nO9BlAKZoIK-mMbiyQzdyyVrSTi2B9c3TGyEQ40M6He_odCxfoeDlIic-yjyqMYyEFyCRy_WOAHcDf2FGe7NNuGH2HTsmYCC337k3l99CO83aWEjfGUlxtJkZSPtsF43x9jMlcJekN7mF0p86U1bZ2M_cj-wKyvib2f-giA74xaTOP5r0dNivURwAX8UebwRRL4srnwqs3UfAwsBiDXa5N0b8xMMMyhBUdelVDqr8x8FTvSUmNa82PrHN3VAde_MaimEzRcbm7d885Q_iOin6AfR4cEw_hhaBRAUv_OK71XTHBPGXeSy-UDaNZMY3XonixANCwUBk-d1uTzuGg98ePwcgx03wY9XZc9vKi5mbvSR2Za9GXRcevAJQ5GBPhGPMt7FCN7vYhcPO2gUdO2P4kOtdJs1R4AK3FRev3JFT9Ruv7W1o1tZNzoIF5ClILk07bVv9gEX7joy7ipGLMJa03vDzG7r_ynCwdrUAystRYkvdMotOlUqAHDRn67dhXi6prToykPq5LiFHg4qt1F0DWUiOsYo81-hTeutwgwAvDPgGwYZDIuK5oEkAuEzoyJ7Ek3pmLQDXxmUg1tcn9xmRniLcOd5ZaH03pU7N1nz9xOuI0NyYOnzYuqr0bVhnlatadytAz5Pj8Nh5vg0lOMGz8nlgCQxv0Aku19QKrCk_DHP1QRkGtdISoPPHUakPaSe5iPq1sH5TrOqZOGrWK-shyqExxpjq-rCHaUv10SYB2XM8cg2wD1cuwfNeFJ8g6NpHc34r8NTVOgD_dOGnI_WKxmomqD7jltALfm-u7NnUGMHQnRNIcQl2NZp8KuQI1jbjHpA3Vz-mBwIoYFbNexeKZxG9fN6PoDb2XFPAQXAx1yXRz3KiCHsbOqhgy2gaXC2opuxKKotjTNFiS0U-SKr8eNZxBjap_PG11F--pqvNgM9LA4wMJrN0Fl3VvrIVKEEkl3CLP8Dq3XBAdno1RuPB1H32CpDU1Rni8pkKKuarTedyOLFEZRKgTbbdEcsdIkPF1yHQqbnh857EAOIQE.n0zsMOeoaBpqK9sleN6CJw" # noqa: E501
    # verify_integrity_token(tokenStr)


if __name__ == "__main__":
    main()
