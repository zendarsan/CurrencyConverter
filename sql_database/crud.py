from sqlalchemy.orm import Session
from . import models, schemas


def get_conversions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Conversion).offset(skip).limit(limit).all()


def create_conversion(db: Session, conversion: schemas.ConversionBase):
    db_conversion = models.Conversion(**conversion)
    db.add(db_conversion)
    db.commit()
    db.refresh(db_conversion)
    return db_conversion

