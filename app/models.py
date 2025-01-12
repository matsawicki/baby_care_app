from app.database import Base
from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
import uuid


class Enum(Base):
    __tablename__ = "enum"

    id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    enum_name = Column(String(100), nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(
        DateTime, default=None, onupdate=datetime.now(timezone.utc)
    )


class EnumHistory(Base):
    __tablename__ = "enum_history"

    id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    enum_id = Column(String(100), nullable=False)
    enum_name = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    valid_from = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    valid_to = Column(
        DateTime
    )
    is_deleted = Column(Boolean, default=False, nullable=False)


class Parent(Base):
    __tablename__ = "parent"

    id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(100), unique=True, nullable=False)
    username = Column(String(100), unique=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100))
    hashed_password = Column(String(100), nullable=False)
    role = Column(String(100), ForeignKey("enum.id"))
    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(
        DateTime, default=None, onupdate=datetime.now(timezone.utc)
    )
    is_deleted = Column(Boolean, default=False, nullable=False)


class Kid(Base):
    __tablename__ = "kid"

    id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100))
    birth_date = Column(DateTime)
    parent_id = Column(String(100), ForeignKey("parent.id"))
    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(
        DateTime, default=None, onupdate=datetime.now(timezone.utc)
    )
    is_deleted = Column(Boolean, default=False, nullable=False)

    parent = relationship("Parent", backref="kid")


class KidPermission(Base):
    __tablename__ = "kid_permission"

    id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    kid_id = Column(String(100), ForeignKey("kid.id"), nullable=False)
    parent_id = Column(String(100), ForeignKey("parent.id"), nullable=False)
    role_id = Column(String(100), ForeignKey("enum.id"), nullable=False)
    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(
        DateTime, default=None, onupdate=datetime.now(timezone.utc)
    )
    is_deleted = Column(Boolean, default=False, nullable=False)

    kid = relationship("Kid", backref="kid_permission")
    parent = relationship("Parent", backref="kid_permission")


class KidInvitation(Base):
    __tablename__ = "kid_invitation"

    id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    kid_id = Column(String(100), ForeignKey("kid.id"), nullable=False)
    inviter_parent_id = Column(String(100), ForeignKey("parent.id"), nullable=False)
    invited_email = Column(String(100), nullable=False)
    role_id = Column(String(100), ForeignKey("enum.id"), nullable=False)
    invitation_token = Column(String(100), unique=True, nullable=False)
    expiration_datetime = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc) + timedelta(hours=72),
        nullable=False,
    )
    is_accepted = Column(Boolean, default=False, nullable=False)
    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    accepted_datetime = Column(DateTime, default=None)
    is_deleted = Column(Boolean, default=False, nullable=False)

    kid = relationship("Kid", backref="kid_invitation")
    inviter = relationship("Parent", backref="kid_invitation")


class Event(Base):
    __tablename__ = "event"

    id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    kid_id = Column(String(100), ForeignKey("kid.id"), nullable=False)
    event_type_id = Column(String(100), ForeignKey("enum.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    string_value = Column(String(255))
    float_value = Column(Float)
    bool_value = Column(Boolean)
    int_value = Column(Integer)
    unit_id = Column(String(100), ForeignKey("enum.id"))

    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(
        DateTime, default=None, onupdate=datetime.now(timezone.utc)
    )
    is_deleted = Column(Boolean, default=False, nullable=False)

    kid = relationship("Kid", backref="event")
