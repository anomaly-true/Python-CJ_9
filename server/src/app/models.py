from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    """Table representing all the users.

    Attributes
    ----------
    id: The user id.
    token: Token to authenticate the.
    username: Username
    password: Password
    is_active: If the user is active or not
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String)
    username = Column(String, index=True, unique=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)

    solutions = relationship("Solution")


class Code(Base):
    """Table representing a game level.

    Attributes
    ----------
    id: The user id.
    title: The title for the level.
    bugged_code: The bugged code for the level.
    documentation: The documentation for how to solve the buggy code.
    tests: The unittest for the buggy code.
    """

    __tablename__ = "codes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    bugged_code = Column(String)
    documentation = Column(String)
    tests = Column(String)


class Solution(Base):  # noqa: D101
    __tablename__ = "solutions"

    id = Column(Integer, primary_key=True, index=True)
    solution = Column(String)
    documentation = Column(String)
    tests = Column(String)
    time = Column(Float, nullable=True)
    memory = Column(Float, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))
