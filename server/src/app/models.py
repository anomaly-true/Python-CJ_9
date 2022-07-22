
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):  # noqa: D101
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)

    solutions = relationship("Solution")


class Code(Base):  # noqa: D101
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
