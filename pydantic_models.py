from pydantic import BaseModel
from datetime import timedelta


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
    time: timedelta


class RefreshTokenPd(BaseModel):
    refresh_token: str


class LeaderboardPd(BaseModel):
    headers: dict
    tables: list


class TestPd(BaseModel):
    text: str


class UserUidPd(BaseModel):
    uid: int


class UserGetDataPd(BaseModel):
    headers: dict
    uid: int


class UserUsernamePd(BaseModel):
    username: str
