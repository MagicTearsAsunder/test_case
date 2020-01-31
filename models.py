from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship


engine = create_engine(
    # TODO
    "postgresql://USERNAME:PASSWORD@localhost/TABLE"
)

Base = declarative_base()


class UsersTable(Base):
    """User model."""

    the_id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    users_picture = relationship('UserPicture')
    __tablename__ = 'users_table'


class UserPicture(Base):
    """User picture model."""

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users_table.the_id'))
    picture = Column(LargeBinary)
    __tablename__ = 'user_picture'


class UserVoice(Base):
    """User voice message model."""

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users_table.the_id'))
    voice = Column(LargeBinary)
    __tablename__ = 'user_voice'


Base.metadata.create_all(engine)
