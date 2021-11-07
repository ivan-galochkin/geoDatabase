from pydantic import BaseModel
from datetime import time


class UserSignUpPd(BaseModel):
    username: str
    email: str
    password: str


class UserSignInPd(BaseModel):
    email: str
    password: str


class QuizResultsPd(BaseModel):
    headers: dict
    quiz: str
    points: int
    time: time


class RefreshTokenPd(BaseModel):
    refresh_token: str


class LeaderboardPd(BaseModel):
    headers: dict


class TestPd(BaseModel):
    text: str


class UserUidPd(BaseModel):
    uid: int


class UserGetDataPd(BaseModel):
    headers: dict
    uid: int


class UserUsernamePd(BaseModel):
    username: str
