from db_session import Base
import sqlalchemy as sa
from sqlalchemy.orm import relationship


class UserSchema(Base):
    __tablename__ = 'users'
    uid = sa.Column(sa.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    username = sa.Column(sa.String, unique=True)
    email = sa.Column(sa.String, unique=True, nullable=False)
    password = sa.Column(sa.String)
    refresh_token = sa.Column(sa.String)

    quiz_results = relationship('QuizResultsSchema')


class QuizResultsSchema(Base):
    __tablename__ = 'quiz_results'
    uid = sa.Column(sa.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    id = sa.Column(sa.Integer, sa.ForeignKey('users.uid'), unique=True, nullable=False)
    # points for every quiz
    usa_states = sa.Column(sa.Integer, default=0)
    serbia_regions = sa.Column(sa.Integer, default=0)
    italy_regions = sa.Column(sa.Integer, default=0)
    # time
    usa_states_time = sa.Column(sa.Time)
    serbia_regions_time = sa.Column(sa.Time)
    italy_regions_time = sa.Column(sa.Time)