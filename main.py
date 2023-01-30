from fastapi import FastAPI, Depends
import requests
import json
from datetime import datetime
from fastapi.security.api_key import APIKey
import authorization
from sqlalchemy.orm import Session
from sql_database import crud, models, schemas
from sql_database.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

COMMON_HEADERS = {
    'Accept': '*/*',
    'Referer': 'https://www.xe.com/currencyconverter/convert/',
    'Accept-Language': 'en-IN,en-GB;q=0.9,en;q=0.8',
    'If-None-Match': '"10ec-Rk1mmUqE9gzCHMHvlkCYNWnAy0g"',
    'Host': 'www.xe.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15',
    'Authorization': 'Basic bG9kZXN0YXI6RDlxT3N3RVg4WEJabjVidGhYRDN5Rk1OOG0yVXE3ZXQ=',
    'Connection': 'keep-alive',
}

@app.get("/convert", dependencies=[Depends(authorization.get_api_key)])
async def convert(amount:float, from_currency:str, to_currency:str, db: Session = Depends(get_db)): #Converts the given amount from the from_currency to the to_currency
    try:
        response = requests.get('https://www.xe.com/api/protected/midmarket-converter/', headers=COMMON_HEADERS, timeout=10)
    except requests.Timeout:
        return {'error': "Request timed out"}

    response_json = json.loads(response.content)
    rates = response_json['rates']
    try: #Check if currencies exist in the data
        to_rate = rates[to_currency]
        from_rate = rates[from_currency]
    except KeyError:
        return {'error': 'Currency does not exist. Please check that the currency codes are valid.'}
    
    to_amount = to_rate * amount / from_rate 
    converted_time = int(str(response_json['timestamp'])[:-3])
    converted_dt = datetime.fromtimestamp(converted_time)
    crud.create_conversion(db, { 
            'converted_amount': to_amount,
            'rate': to_rate/from_rate,
            "time_of_conversion": converted_dt,
            "from_currency": from_currency,
            "to_currency": to_currency
            } 
        )

    return { 
            'converted_amount': to_amount,
            'rate': to_rate,
            "metadata_":{
                "time_of_conversion": converted_dt,
                "from_currency": from_currency,
                "to_currency": to_currency
            } 
        }   
    
    


@app.get("/currencies", dependencies=[Depends(authorization.get_api_key)])
async def get_currencices(): #Returns a list of all currencies from the xe website
    try:
        response = requests.get('https://www.xe.com/_next/data/zXvi01CWf5uhNGPHQuwm0/en/apps.json', headers=COMMON_HEADERS, timeout=10)
    except requests.Timeout:
        return {'error': "Request timed out"}

    data = json.loads(response.content)
    currency_data = data['pageProps']['commonI18nResources']['currencies']['en']
    currency_codes = {currency_data[x]['name']:x for x in currency_data.keys()}
    return currency_codes

@app.get("/history", dependencies=[Depends(authorization.get_api_key)])
async def history(db: Session = Depends(get_db)): #Returns a history of all the conversions done so far. 
    
    conversions_db:list[schemas.ConversionRead] = crud.get_conversions(db)
    formatted_conversions = []
    for conversion in conversions_db:
        formatted_conversions.append({ 
            'converted_amount': conversion.converted_amount,
            'rate': conversion.rate,
            "metadata_":{
                "time_of_conversion": conversion.time_of_conversion,
                "from_currency": conversion.from_currency,
                "to_currency": conversion.to_currency
            } 
        })

    return formatted_conversions

