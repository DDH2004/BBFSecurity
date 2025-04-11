from fastapi import HTTPException
import requests

class AuthService:
    def __init__(self, auth0_domain: str, auth0_client_id: str, auth0_client_secret: str):
        self.auth0_domain = auth0_domain
        self.auth0_client_id = auth0_client_id
        self.auth0_client_secret = auth0_client_secret

    def register_user(self, email: str, password: str):
        url = f"https://{self.auth0_domain}/dbconnections/signup"
        payload = {
            "client_id": self.auth0_client_id,
            "email": email,
            "password": password,
            "connection": "Username-Password-Authentication"
        }
        response = requests.post(url, json=payload)
        if response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()

    def login_user(self, email: str, password: str):
        url = f"https://{self.auth0_domain}/oauth/token"
        payload = {
            "client_id": self.auth0_client_id,
            "username": email,
            "password": password,
            "grant_type": "password",
            "scope": "openid"
        }
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()

    def get_user_info(self, token: str):
        url = f"https://{self.auth0_domain}/userinfo"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()