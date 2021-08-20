import sqlalchemy.exc
from fastapi import FastAPI, Header, HTTPException
from pydantic_models import UserPd
import fastapi
from db_session import create_session, global_init
import sqlalchemy as sa
from os import environ
from schemas import UserSchema
from fastapi.middleware.cors import CORSMiddleware
import datetime as dt
import uvicorn
from password_service import verify_password, make_hashed_password
from jwt_service import create_answer

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


def create_user(user: UserPd):
    new_user = UserSchema()
    new_user.email = user.email
    new_user.password = make_hashed_password(user.password)
    return new_user


@app.post("/users/sign_in", status_code=200)
def sign_in(user: UserPd):
    session = create_session()
    try:
        db_user = session.query(UserSchema).filter(UserSchema.email == user.email).one()
        if not verify_password(user.password, db_user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return create_answer(db_user)
    except sqlalchemy.exc.NoResultFound:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    finally:
        session.close()


@app.post("/users/sign_up", status_code=200)
def sign_up(user: UserPd):
    session = create_session()
    try:
        session.add(create_user(user))
        session.commit()
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(status_code=422, detail="User already registered")
    finally:
        session.close()


uvicorn.run(app, host="127.0.0.1", port=8000)
