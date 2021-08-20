from db_session import Base
import sqlalchemy as sa


class UserSchema(Base):
    __tablename__ = 'users'
    uid = sa.Column(sa.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    email = sa.Column(sa.String, unique=True, nullable=False)
    password = sa.Column(sa.String, nullable=False)
