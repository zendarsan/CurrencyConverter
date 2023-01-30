from pydantic import BaseModel

class ConversionBase(BaseModel):
    converted_amount: float
    rate: float
    time_of_conversion: int
    from_currency: str
    to_currency: str

class ConversionRead(ConversionBase):
    id: int
    class Config:
        orm_mode = True

