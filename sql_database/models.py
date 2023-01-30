from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from .database import Base


class Conversion(Base):
    __tablename__ = "conversions"

    id = Column(Integer, primary_key=True, index=True)
    converted_amount = Column(Float)
    rate = Column(Float)
    time_of_conversion = Column(DateTime)
    from_currency = Column(String)
    to_currency = Column(String)

