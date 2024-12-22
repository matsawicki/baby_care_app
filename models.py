from database import Base
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship, backref


class Parent(Base):
    __tablename__ = "parents"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100))
    hashed_password = Column(String, nullable=False)
    role = Column(Integer, ForeignKey("role_dicts.id"))  # points to RoleDict
    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(
        DateTime, default=None, onupdate=datetime.now(timezone.utc)
    )
    is_deleted = Column(Boolean, default=False, nullable=False)

    role_obj = relationship("RoleDict", backref="parents")


class KidPermission(Base):
    """
    Once an invitation is accepted, this table tracks which parent/guardian
    has what role/permission on a given kid.
    """

    __tablename__ = "kid_permissions"

    id = Column(Integer, primary_key=True)
    kid_id = Column(Integer, ForeignKey("kids.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("parents.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("role_dicts.id"), nullable=False)
    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(
        DateTime, default=None, onupdate=datetime.now(timezone.utc)
    )
    is_deleted = Column(Boolean, default=False, nullable=False)

    kid = relationship("Kid", backref="permissions")
    parent = relationship("Parent", backref="kid_permissions")
    role_obj = relationship("RoleDict", backref="kid_permissions")


class KidInvitation(Base):
    """
    Holds invitations for a parent or any user to gain access to a kid.
    The inviter defines the role (from RoleDict) and invites by email.
    Once accepted, an entry in KidPermission can be created.
    """

    __tablename__ = "kid_invitations"

    id = Column(Integer, primary_key=True)
    kid_id = Column(Integer, ForeignKey("kids.id"), nullable=False)
    inviter_parent_id = Column(Integer, ForeignKey("parents.id"), nullable=False)
    invited_email = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("role_dicts.id"), nullable=False)
    invitation_token = Column(String, unique=True, nullable=False)
    is_accepted = Column(Boolean, default=False, nullable=False)

    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    accepted_datetime = Column(DateTime, default=None)
    is_deleted = Column(Boolean, default=False, nullable=False)

    kid = relationship("Kid", backref="invitations")
    inviter = relationship("Parent", backref="sent_invitations")
    role_obj = relationship("RoleDict", backref="kid_invitations")


class RoleDict(Base):
    __tablename__ = "roles_dict"

    id = Column(Integer, primary_key=True)
    role_name = Column(String, nullable=False)
    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(
        DateTime, default=None, onupdate=datetime.now(timezone.utc)
    )
    is_deleted = Column(Boolean, default=False)


class Kid(Base):
    __tablename__ = "kids"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100))
    birth_date = Column(DateTime)
    parent_id = Column(Integer, ForeignKey("parents.id"))
    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(
        DateTime, default=None, onupdate=datetime.now(timezone.utc)
    )
    is_deleted = Column(Boolean, default=False, nullable=False)

    parent = relationship("Parent", backref="kids")


class KidStaticDetailDict(Base):
    """
    Dictionary table for 'type' of static detail, e.g., 'Height', 'Weight', etc.
    """

    __tablename__ = "kid_static_details_dict"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(
        DateTime, default=None, onupdate=datetime.now(timezone.utc)
    )
    is_deleted = Column(Boolean, default=False, nullable=False)


class KidStaticDetail(Base):
    __tablename__ = "kid_static_details"

    id = Column(Integer, primary_key=True)
    quantity = Column(Float, nullable=False)
    unit_id = Column(Integer, ForeignKey("unit_dicts.id"), nullable=False)
    kid_id = Column(Integer, ForeignKey("kids.id"), nullable=False)
    # Reference to kid_static_detail_dict
    detail_type_id = Column(
        Integer, ForeignKey("kid_static_detail_dicts.id"), nullable=True
    )

    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(
        DateTime, default=None, onupdate=datetime.now(timezone.utc)
    )
    is_deleted = Column(Boolean, default=False, nullable=False)

    unit = relationship("UnitDict", backref="kid_static_details")
    kid = relationship("Kid", backref="static_details")
    detail_type = relationship("KidStaticDetailDict", backref="static_details")


class KidEventDict(Base):
    __tablename__ = "kid_events_dict"

    id = Column(Integer, primary_key=True)
    event_name = Column(String, nullable=False)
    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(
        DateTime, default=None, onupdate=datetime.now(timezone.utc)
    )
    is_deleted = Column(Boolean, default=False, nullable=False)


class UnitDict(Base):
    __tablename__ = "units_dicts"

    id = Column(Integer, primary_key=True)
    unit_name = Column(String, nullable=False)
    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(
        DateTime, default=None, onupdate=datetime.now(timezone.utc)
    )
    is_deleted = Column(Boolean, default=False, nullable=False)


class KidEvent(Base):
    __tablename__ = "kid_events"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("kid_event_dicts.id"), nullable=False)
    kid_id = Column(Integer, ForeignKey("kids.id"), nullable=False)

    timestamp = Column(DateTime, nullable=False)
    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(
        DateTime, default=None, onupdate=datetime.now(timezone.utc)
    )
    is_deleted = Column(Boolean, default=False, nullable=False)

    event_type = relationship("KidEventDict", backref="kid_events")
    kid = relationship("Kid", backref="events")


class PooEvent(Base):
    __tablename__ = "poo_events"

    id = Column(Integer, primary_key=True)
    kids_event_id = Column(
        Integer, ForeignKey("kid_events.id"), nullable=False, unique=True
    )
    # e.g., True if poo happened
    value = Column(Boolean, nullable=False)

    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(
        DateTime, default=None, onupdate=datetime.now(timezone.utc)
    )
    is_deleted = Column(Boolean, default=False, nullable=False)

    kids_event = relationship("KidEvent", backref=backref("poo_detail", uselist=False))


class PissEvent(Base):
    __tablename__ = "piss_events"

    id = Column(Integer, primary_key=True)
    kids_event_id = Column(
        Integer, ForeignKey("kid_events.id"), nullable=False, unique=True
    )
    unit_id = Column(Integer, ForeignKey("unit_dicts.id"), nullable=False)
    value = Column(Float, nullable=False)  # Amount of piss measured

    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(
        DateTime, default=None, onupdate=datetime.now(timezone.utc)
    )
    is_deleted = Column(Boolean, default=False, nullable=False)

    kids_event = relationship("KidEvent", backref=backref("piss_detail", uselist=False))
    unit = relationship("UnitDict")


class FeedingEvent(Base):
    __tablename__ = "feeding_events"

    id = Column(Integer, primary_key=True)
    kids_event_id = Column(
        Integer, ForeignKey("kid_events.id"), nullable=False, unique=True
    )
    unit_id = Column(Integer, ForeignKey("unit_dicts.id"), nullable=False)
    amount = Column(Float, nullable=False)  # e.g. milliliters of milk

    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(
        DateTime, default=None, onupdate=datetime.now(timezone.utc)
    )
    is_deleted = Column(Boolean, default=False, nullable=False)

    kids_event = relationship(
        "KidEvent", backref=backref("feeding_detail", uselist=False)
    )
    unit = relationship("UnitDict")


class SaturationEvent(Base):
    __tablename__ = "saturation_events"

    id = Column(Integer, primary_key=True)
    kids_event_id = Column(
        Integer, ForeignKey("kid_events.id"), nullable=False, unique=True
    )
    saturation_value = Column(Float, nullable=False)  # e.g. O2 saturation %

    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(
        DateTime, default=None, onupdate=datetime.now(timezone.utc)
    )
    is_deleted = Column(Boolean, default=False, nullable=False)

    kids_event = relationship(
        "KidEvent", backref=backref("saturation_detail", uselist=False)
    )
