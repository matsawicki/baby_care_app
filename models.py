from database import Base
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship, backref


class Parents(Base):
    __tablename__ = "parents"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100))
    hashed_password = Column(String, nullable=False)
    role = Column(Integer, ForeignKey("roles_dict.id"))
    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(DateTime)
    id_deleted = Column(Boolean, default=False, nullable=False)

    role_obj = relationship("RolesDict", backref="parents")


class RolesDict(Base):
    __tablename__ = "roles_dict"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String, nullable=False)
    is_deleted = Column(Boolean, default=False)


class Kids(Base):
    __tablename__ = "kids"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100))
    birth_date = Column(DateTime)
    parent_id = Column(Integer, ForeignKey("parents.id"))
    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(DateTime)
    id_deleted = Column(Boolean, default=False, nullable=False)

    parent = relationship("Parents", backref="kids")


class KidsStaticDetails(Base):
    __tablename__ = "kids_static_details"

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Float, nullable=False)
    unit_id = Column(Integer, ForeignKey("units_dict.id"), nullable=False)
    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(DateTime)
    kid_id = Column(Integer, ForeignKey("kids.id"), nullable=False)

    unit = relationship("UnitsDict", backref="kids_static_details")
    kid = relationship("Kids", backref="static_details")


class KidsStaticDetailsDict(Base):
    __tablename__ = "kids_static_details_dict"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)


class KidsEventsDict(Base):
    __tablename__ = "kids_event_dict"

    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    # Possible values for event_name: "poo", "piss", "feeding", "saturation"


class UnitsDict(Base):
    __tablename__ = "units_dict"

    id = Column(Integer, primary_key=True, index=True)
    unit_name = Column(String, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)


class KidsEvents(Base):
    __tablename__ = "kids_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("kids_event_dict.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(DateTime)
    is_deleted = Column(Boolean, default=False, nullable=False)

    event_type = relationship("KidsEventsDict", backref="events")


class PooEvents(Base):
    __tablename__ = "poo_events"

    id = Column(Integer, primary_key=True, index=True)
    kids_event_id = Column(
        Integer, ForeignKey("kids_events.id"), nullable=False, unique=True
    )
    value = Column(Boolean, nullable=False)  # True if poo happened, for example
    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(DateTime)
    is_deleted = Column(Boolean, default=False, nullable=False)
    kids_event = relationship(
        "KidsEvents", backref=backref("poo_detail", uselist=False)
    )


class PissEvents(Base):
    __tablename__ = "piss_events"

    id = Column(Integer, primary_key=True, index=True)
    kids_event_id = Column(
        Integer, ForeignKey("kids_events.id"), nullable=False, unique=True
    )
    unit_id = Column(Integer, ForeignKey("units_dict.id"), nullable=False)
    value = Column(Float, nullable=False)  # Amount of piss measured
    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(DateTime)
    is_deleted = Column(Boolean, default=False, nullable=False)

    kids_event = relationship(
        "KidsEvents", backref=backref("piss_detail", uselist=False)
    )
    unit = relationship("UnitsDict")


class FeedingEvents(Base):
    __tablename__ = "feeding_events"

    id = Column(Integer, primary_key=True, index=True)
    kids_event_id = Column(
        Integer, ForeignKey("kids_events.id"), nullable=False, unique=True
    )
    unit_id = Column(Integer, ForeignKey("units_dict.id"), nullable=False)
    amount = Column(Float, nullable=False)  # e.g. milliliters of milk
    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(DateTime)
    is_deleted = Column(Boolean, default=False, nullable=False)
    kids_event = relationship(
        "KidsEvents", backref=backref("feeding_detail", uselist=False)
    )
    unit = relationship("UnitsDict")


class SaturationEvents(Base):
    __tablename__ = "saturation_events"

    id = Column(Integer, primary_key=True, index=True)
    kids_event_id = Column(
        Integer, ForeignKey("kids_events.id"), nullable=False, unique=True
    )
    saturation_value = Column(Float, nullable=False)  # e.g. O2 saturation %
    created_datetime = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    modified_datetime = Column(DateTime)
    is_deleted = Column(Boolean, default=False, nullable=False)
    kids_event = relationship(
        "KidsEvents", backref=backref("saturation_detail", uselist=False)
    )
