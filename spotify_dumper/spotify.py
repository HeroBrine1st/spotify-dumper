import base64
import json
import os
import re
import socket
import time
import urllib.parse
import webbrowser
from typing import Optional

from requests import Session


class SpotifyAPI:
    token_deadline: Optional[float]
    access_token: Optional[str]
    refresh_token: Optional[str]

    def __init__(self, client_id: str, client_secret: str, listen_port: int):
        self.session = Session()
        self.access_token = None
        self.refresh_token = None
        self.token_deadline = None
        self.client_id = client_id
        self.client_secret = client_secret
        self.listen_port = listen_port
        self.client_id_header = "Basic " + base64.b64encode(f"{self.client_id}:{self.client_secret}".encode("utf-8")) \
            .decode("utf-8")

    @classmethod
    def new(cls, listen_port: int, client_id: Optional[str] = None, client_secret: Optional[str] = None,
            keep: bool = False):
        data = None
        if os.path.exists("data.json"):
            with open("data.json") as f:
                data = json.load(f)

        if client_id is None or client_secret is None:
            if data is None:
                raise NoApiPairError
            elif "client_id" not in data or "client_secret" not in data:
                raise NoApiPairError
            client_id = data["client_id"]
            client_secret = data["client_secret"]
        res = cls(listen_port=listen_port, client_id=client_id, client_secret=client_secret)
        if data:
            res.restore(data)
        else:
            res.auth()
        if res.token_deadline < time.time():
            res.refresh()
        if keep or data:
            data = res.save()
            data["client_id"] = client_id
            data["client_secret"] = client_secret
            with open("data.json", "w") as f:
                json.dump(data, f)
        return res

    def restore(self, data: dict):
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        self.token_deadline = data["token_deadline"]

    def save(self):
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_deadline": self.token_deadline
        }

    def auth(self):
        webbrowser.open(
            "https://accounts.spotify.com/authorize?"
            + urllib.parse.urlencode({
                "response_type": "code",
                "client_id": self.client_id,
                "scope": "playlist-read-private playlist-read-collaborative user-library-read",
                "redirect_uri": f"http://localhost:{self.listen_port}/callback",
            })
        )
        # region Handle incoming request in-place
        # With any library I would have to use threading.Event or something, because
        # no library lets you handle request in-place.
        with socket.socket() as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('127.0.0.1', self.listen_port))
            sock.listen()
            while True:
                sock2, _ = sock.accept()
                with sock2:
                    buffer = b""
                    # https://docs.python.org/3/library/socket.html#socket.socket.recv
                    # WHAT DOES HAPPEN WHEN NO DATA AVAILABLE ??????
                    while b"\r\n\r\n" not in buffer:
                        buffer += sock2.recv(4096)
                    request_line_end = buffer.find(b"\r\n")
                    if request_line_end == -1:
                        continue
                    request_line = buffer[0:request_line_end].decode("utf-8")
                    method, path, version = request_line.split(" ")
                    # RFC 2616: case sensitive
                    if method != "GET":
                        continue
                    # We do not support HTTP/2
                    assert version in ["HTTP/1.1", "HTTP/1.0"]
                    sock2.sendall(b"HTTP/1.0 200 OK\r\n"
                                  b"Content-Type: text/html\r\n"
                                  b"\r\n"
                                  b'<script>close()</script>You can close this window.')
                    code = re.search('code=([^&]+)', path).group(1)
                    break
        # endregion
        resp = self.session.post(
            "https://accounts.spotify.com/api/token",
            data=urllib.parse.urlencode({
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": f"http://localhost:{self.listen_port}/callback",
            }),
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": self.client_id_header
            }
        )
        resp.raise_for_status()
        data = resp.json()
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        self.token_deadline = int(time.time()) + data["expires_in"]

    def refresh(self):
        resp = self.session.post(
            "https://accounts.spotify.com/api/token",
            data=urllib.parse.urlencode({
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token
            }),
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": self.client_id_header
            }
        )
        resp.raise_for_status()
        data = resp.json()
        self.access_token = data["access_token"]
        self.token_deadline = int(time.time()) + data["expires_in"]

    def get(self, path, params=None):
        if params is None:
            params = {}
        url = path if path.startswith("https://api.spotify.com/v1/") \
            else "https://api.spotify.com/v1/" + path.removeprefix("/")
        resp = self.session.get(
            url,
            headers={"Authorization": f"Bearer {self.access_token}"},
            params=params
        )
        resp.raise_for_status()
        return resp.json()

    def iterate(self, url, params=None):
        if params is None:
            params = {}
        response = self.get(url, params)
        yield response

        while response["next"]:
            response = self.get(response['next'])
            yield response

class NoApiPairError(Exception):
    pass