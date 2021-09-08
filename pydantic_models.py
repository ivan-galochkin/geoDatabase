from pydantic import BaseModel


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


class RefreshTokenPd(BaseModel):
    refresh_token: str


class LeaderboardPd(BaseModel):
    headers: dict
    tables: list
