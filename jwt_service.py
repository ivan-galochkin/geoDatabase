import os
import time
from schemas import UserSchema
from db_session import create_session
import jwt

JWT_SECRET = os.environ["JWT_SECRET"]


def create_access_jwt(user_id: int):
    payload = {
        "user_id": user_id,
        "exp": time.time() + 600
    }
    access_token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    return access_token


def create_refresh_jwt(user_id: int):
    payload = {
        "user_id": user_id,
        "type": "refresh"
    }
    refresh_token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    return refresh_token


def create_answer(user):
    delattr(user, "password")
    return {"tokens": {"access_token": create_access_jwt(user.uid), "refresh_token": create_refresh_jwt(user.uid)},
            "user": user}


def decode_jwt(token):
    try:
        jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        pass
