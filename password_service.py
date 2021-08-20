from schemas import UserSchema
from pydantic_models import UserPd
from db_session import create_session
from passlib.hash import pbkdf2_sha256


def verify_password(plain_password, hashed_password):
    return pbkdf2_sha256.verify(plain_password, hashed_password)


def make_hashed_password(password):
    return pbkdf2_sha256.hash(password)


def get_hashed_password(user: UserPd):
    session = create_session()
    hashed_password = session.query(UserSchema).filter(UserSchema.email == user.email)
    session.close()
    return hashed_password

