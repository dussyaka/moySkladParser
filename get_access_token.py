from parser import MAIN_URL
import base64
import requests
from dotenv import load_dotenv
from os import environ

def get_access_token(login: str, password: str):

    url = MAIN_URL + "/security/token"
    credential_bytes   = f"{login}:{password}".encode("utf-8")
    encoded_bytes      = base64.b64encode(credential_bytes)
    encoded_str        = encoded_bytes.decode("ascii")
    
    headers = {
        'Authorization': 'Basic ' + encoded_str,
        'Accept-Encoding': 'gzip'
    }
    response = requests.post(
        url,
        headers=headers
    )

    if not response.ok:
        print(response.status_code, response.content)
        return

    response_json = response.json()
    access_token = response_json.get('access_token')

    print(f'Токен успешно получен. Токен: {access_token}')

    return access_token

load_dotenv()

login = environ.get('LOGIN')
password = environ.get('PASSWORD')

access_token = get_access_token(login, password)