import jwt
import sqlalchemy.exc
from fastapi import FastAPI, Header, HTTPException

import jwt_service
from pydantic_models import *
from db_session import create_session, global_init
from schemas import UserSchema, QuizResultsSchema
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from password_service import verify_password, make_hashed_password
from jwt_service import create_response, decode_jwt, create_refresh_jwt
import platform

app = FastAPI()

global_init()

origins = ["*"]

tables_realised_str = "usa_states, serbia_regions, italy_regions"
tables_realised_list = ["usa_states", "serbia_regions", "italy_regions"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_leaderboard():
    session = create_session()
    try:
        response = {}
        for table in tables_realised_list:
            users = session.execute(
                f"SELECT username, {table}, {table + '_time'} FROM quiz_results JOIN users u on u.uid = quiz_results.id WHERE {table + '_time'} "
                f"IS NOT NULL "
                f"ORDER BY {table} DESC, {table + '_time'} ASC LIMIT 10").fetchall()
            response[table] = users

        return response
    except sqlalchemy.exc.NoResultFound:
        return "402"
    finally:
        session.close()


def create_user(user: UserSignUpPd):
    new_user = UserSchema()
    new_user.username = user.username
    new_user.email = user.email
    new_user.password = make_hashed_password(user.password)
    new_user.quiz_results = [QuizResultsSchema()]
    return new_user


def check_access_token(payload):
    access_token = payload.headers["access_token"]
    decoded_token = decode_jwt(access_token)
    if decoded_token == "expired":
        raise HTTPException(status_code=401, detail="token expired")
    elif decoded_token == "wrong token":
        raise HTTPException(status_code=401, detail="wrong token")

    return decoded_token


def change_refresh_token(uid: int):
    session = create_session()

    try:
        user = session.query(UserSchema).filter(UserSchema.uid == uid).one()
        user.refresh_token = create_refresh_jwt(uid)
        session.commit()
    except sqlalchemy.exc.NoResultFound:
        pass
    finally:
        session.close()


def get_total_points(uid):
    session = create_session()
    try:
        return sum(
            list(session.execute(f"SELECT {tables_realised_str} FROM quiz_results WHERE uid = {uid}").fetchall()[0]))
    except sqlalchemy.exc.NoResultFound:
        pass


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
    decoded_token = check_access_token(results)
    session = create_session()
    try:
        db_results = session.query(QuizResultsSchema).filter(QuizResultsSchema.id == decoded_token["user_id"]).one()
        previous_points = getattr(db_results, results.quiz)
        previous_time = getattr(db_results, results.quiz + "_time")
        if results.points > previous_points or previous_time is None:
            setattr(db_results, results.quiz, results.points)
            setattr(db_results, results.quiz + "_time", results.time)
            session.commit()
            return "new record"
        elif results.points == previous_points and results.time < previous_time:
            setattr(db_results, results.quiz + "_time", results.time)
            session.commit()
            return "best time"
        session.commit()
        return "no changes"
    except sqlalchemy.exc.NoResultFound:
        raise HTTPException(status_code=422, detail="server_error")
    finally:
        session.close()


@app.post("/users/refresh-token")
def send_tokens(payload: RefreshTokenPd):
    refresh_token = payload.refresh_token
    try:
        jwt_service.decode_jwt(refresh_token)
    except BaseException:
        raise HTTPException(401, "fake token")
    session = create_session()
    try:
        db_user = session.query(UserSchema).filter(UserSchema.refresh_token == refresh_token).one()

        response = create_response(db_user)
        db_user.refresh_token = response['tokens']['refresh_token']
        session.commit()

        return response
    except sqlalchemy.exc.NoResultFound:
        # change_refresh_token(jwt.decode(payload.refresh_token)['user_id'])
        raise HTTPException(403, "relogin")


@app.post("/users/leaderboard")
def send_leaderboard(payload: LeaderboardPd):
    return create_leaderboard()


@app.post("/users/total-points")
def send_total_points(payload: UserGetDataPd):
    return get_total_points(payload.uid)


@app.post("/users/all_results")
def send_all_results(payload: UserGetDataPd):
    session = create_session()
    try:
        data = session.query(QuizResultsSchema).filter(QuizResultsSchema.id == payload.uid).one()
        response = {}
        for column in list(vars(data).keys())[1:]:
            if "id" not in column:
                if "time" in column:
                    try:
                        response[column.replace("_time", "")]
                    except KeyError:
                        response[column.replace("_time", "")] = {}
                    response[column.replace("_time", "")]["time"] = getattr(data, column)
                else:
                    try:
                        response[column]
                    except KeyError:
                        response[column] = {}
                    response[column]["points"] = getattr(data, column)
        return response
    except sqlalchemy.exc.NoResultFound:
        pass
    finally:
        session.close()


@app.post("/test")
def test(payload: TestPd):
    print(payload)
    return "ok"


@app.post("/users/user-data")
def send_user_data(payload: UserUsernamePd):
    session = create_session()
    try:
        user = session.query(UserSchema).filter(UserSchema.username == payload.username).one()
        return {"username": user.username, "uid": user.uid}
    except sqlalchemy.exc.NoResultFound:
        raise HTTPException(404)


host = "0.0.0.0"
if platform.system() == "Darwin":
    host = "localhost"

uvicorn.run(app, host=host, port=8000, debug=True)
