import sqlalchemy.exc
from fastapi import FastAPI, Header, HTTPException
from pydantic_models import *
import fastapi
from db_session import create_session, global_init
import sqlalchemy as sa
from os import environ
from schemas import UserSchema, QuizResultsSchema
from fastapi.middleware.cors import CORSMiddleware
import datetime as dt
import uvicorn
from password_service import verify_password, make_hashed_password
from jwt_service import create_response, decode_jwt

app = FastAPI()

global_init('db.sqlite')

origins = [
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_user(user: UserSignUpPd):
    new_user = UserSchema()
    new_user.username = user.username
    new_user.email = user.email
    new_user.password = make_hashed_password(user.password)
    new_user.quiz_results = [QuizResultsSchema()]
    return new_user


@app.post("/users/sign_in", status_code=200)
def sign_in(user: UserSignInPd):
    session = create_session()
    try:
        db_user = session.query(UserSchema).filter(UserSchema.email == user.email).one()
        if not verify_password(user.password, db_user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        response = create_response(db_user)
        db_user.refresh_token = response['tokens']['refresh_token']
        session.commit()
        return response
    except sqlalchemy.exc.NoResultFound:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    finally:
        session.close()


@app.post("/users/sign_up", status_code=200)
def sign_up(user: UserSignUpPd):
    session = create_session()
    try:
        session.add(create_user(user))
        session.commit()
    except sqlalchemy.exc.IntegrityError as exc:
        if "username" in str(exc.orig):
            detail = "username already in use"
        else:
            detail = "email already in use"
        raise HTTPException(status_code=422, detail=detail)
    finally:
        session.close()


@app.post("/api/quiz-results")
def quiz_results(results: QuizResultsPd):
    access_token = results.headers["access_token"]
    decoded_token = decode_jwt(access_token)
    if decoded_token == "expired":
        raise HTTPException(status_code=401, detail="token expired")
    elif decoded_token == "wrong token":
        raise HTTPException(status_code=401, detail="wrong token")

    session = create_session()
    try:
        db_results = session.query(QuizResultsSchema).filter(decoded_token["user_id"] == QuizResultsSchema.id).one()
        db_points = getattr(db_results, results.quiz)
        db_points = results.points
        session.commit()
    except BaseException as exc:
        print(exc)
    finally:
        session.close()


@app.post("/users/refresh-token")
def send_tokens(payload: RefreshTokenPd):
    refresh_token = payload.refresh_token
    session = create_session()
    try:
        db_user = session.query(UserSchema).filter(UserSchema.refresh_token == refresh_token).one()

        response = create_response(db_user)
        db_user.refresh_token = response['tokens']['refresh_token']

        return response
    except sqlalchemy.exc.NoResultFound:
        raise HTTPException(status_code=401, detail='refresh_token expired')


uvicorn.run(app, host="127.0.0.1", port=8000)
