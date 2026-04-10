from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
import datetime


class Salon(Base):
    __tablename__ = "salons"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(String)

    services = relationship("Service", back_populates="salon")
    staff = relationship("Staff", back_populates="salon")
    bookings = relationship("Booking", back_populates="salon")
    admin_users = relationship("AdminUser", back_populates="salon")


class AdminUser(Base):
    """Admin user for JWT-based dashboard authentication."""
    __tablename__ = "admin_users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    salon_id = Column(Integer, ForeignKey("salons.id"))

    salon = relationship("Salon", back_populates="admin_users")


class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    salon_id = Column(Integer, ForeignKey("salons.id"))
    name = Column(String, index=True)
    duration_minutes = Column(Integer)
    price = Column(Float)
    description = Column(String, nullable=True)

    salon = relationship("Salon", back_populates="services")


class Staff(Base):
    __tablename__ = "staff"
    id = Column(Integer, primary_key=True, index=True)
    salon_id = Column(Integer, ForeignKey("salons.id"))
    name = Column(String)
    working_hours = Column(String)

    salon = relationship("Salon", back_populates="staff")
    bookings = relationship("Booking", back_populates="staff")


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    salon_id = Column(Integer, ForeignKey("salons.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    staff_id = Column(Integer, ForeignKey("staff.id"))
    customer_name = Column(String)
    customer_phone = Column(String)
    customer_email = Column(String, nullable=True, default="")
    appointment_time = Column(DateTime)
    status = Column(String, default="confirmed")  # confirmed, cancelled, completed

    salon = relationship("Salon", back_populates="bookings")
    staff = relationship("Staff", back_populates="bookings")
    review = relationship("Review", back_populates="booking", uselist=False)


class Review(Base):
    """Customer review tied to a specific booking."""
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), unique=True)
    service_id = Column(Integer, ForeignKey("services.id"))
    salon_id = Column(Integer, ForeignKey("salons.id"))
    customer_name = Column(String)
    rating = Column(Integer)  # 1–5
    comment = Column(Text, default="")

    booking = relationship("Booking", back_populates="review")


class CallLog(Base):
    """Track voice calls via Exotel with full booking details."""
    __tablename__ = "call_logs"
    id = Column(Integer, primary_key=True, index=True)
    call_sid = Column(String, unique=True, index=True)
    from_number = Column(String)
    to_number = Column(String)
    direction = Column(String, default="incoming")  # incoming, outgoing
    status = Column(String, default="initiated")  # initiated, ringing, in-progress, completed, failed, transferred
    salon_id = Column(Integer, ForeignKey("salons.id"), nullable=True)
    customer_name = Column(String, nullable=True)
    
    # AI conversation tracking
    ai_transcript = Column(Text, default="")
    ai_response = Column(Text, default="")
    
    # Recording
    recording_url = Column(String, nullable=True)
    recording_duration = Column(Integer, nullable=True)
    
    # Booking details (captured during call)
    service = Column(String, nullable=True)  # haircut, facial, etc.
    date = Column(String, nullable=True)     # YYYY-MM-DD
    time = Column(String, nullable=True)     # HH:MM AM/PM
    stylist = Column(String, nullable=True)  # Priya, Rahul, etc.
    phone = Column(String, nullable=True)    # Customer phone from booking
    booking_reference = Column(String, nullable=True)  # BK123456
    
    # Transfer info
    transferred_to = Column(String, nullable=True)
    
    # SMS tracking
    sms_sent = Column(Boolean, default=False)
    sms_message = Column(Text, default="")
    
    # Custom data from passthru
    custom_data = Column(String, nullable=True)
    
    # Duration tracking
    duration = Column(Integer, default=0)  # seconds
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    answered_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    
    salon = relationship("Salon")


class CallRecording(Base):
    """Store call recording references."""
    __tablename__ = "call_recordings"
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("call_logs.id"))
    recording_url = Column(String)
    duration = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    call = relationship("CallLog")
