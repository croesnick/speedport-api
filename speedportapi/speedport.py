import logging
import time
import requests
import hashlib
import re


logger = logging.getLogger(__name__)


class LoginError(Exception):
    pass


class Speedport:
    ENDPOINT_BACKUP = 'data/backup.json'
    ENDPOINT_LOGIN = 'data/Login.json'
    INIT_CSRF = 'nulltoken'

    def __init__(self, host, password):
        self.host = host
        self.challenge = self.challenge(self.host)
        self.password_hash = self.password_hash(password, self.challenge)
        self.cookies = None

    @staticmethod
    def password_hash(password, challenge):
        # Create a sha256 sum of the password+challenge
        return hashlib.sha256(challenge.encode() + ":".encode() + password.encode()).hexdigest()

    @staticmethod
    def get_json_value(data, id):
        for item in data:
            if item["varid"] == id:
                return item["varvalue"]
        return None

    def login(self):
        self._login(self.password_hash, self.challenge)

    def challenge(self, host):
        params = {
            '_time': round(time.time() * 1000),
            '_rand': 666,
            'csrf_token': self.INIT_CSRF,
        }
        r = requests.get(f'http://{self.host}/data/Login.json', params=params)

        data = r.json()

        challenge = self.get_json_value(data, "challenge")
        if challenge is not None:
            return challenge

        # On newer Firmware the challenge is embedded in the html page
        r = requests.get(f'http://{host}/html/_login/index.html')
        # We assume that there will be only one challenge embedded in the index.html
        challenge = re.findall(r'challenge = \"([A-Za-z0-9]+)\"', r.text)[0]
        if challenge is not None:
            return challenge

        return None

    def backup(self):
        resp = self._request(self.cookies, self.ENDPOINT_BACKUP)
        return resp.content if resp.ok else None

    def _request(self, cookie, path):
        return requests.get(f'http://{self.host}/{path}', cookies=cookie)

    def _login(self, password_hash, challenge):
        logger.info(f'Login with password_hash={password_hash} and challenge={challenge} to '
                    f'host={self.host}')
        # Send a post request to the Login.json which contains the `password_hash` and the static
        # csrf token
        r = requests.post(f'http://{self.host}/data/Login.json',
                          data={
                              'password': password_hash,
                              'showpw': 0,
                              'csrf_token': self.INIT_CSRF,
                              'challengev': challenge,
                          })

        self.cookies = r.cookies
        r = self._request(self.cookies, self.ENDPOINT_LOGIN)
        if r is None or self.get_json_value(r.json(), "login") != "true":
            raise LoginError(r.json())
