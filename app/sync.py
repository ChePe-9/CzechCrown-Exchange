import requests
from datetime import datetime, timedelta
from .database import get_db, ExchangeRate
from .config import settings
from .utils import parse_exchange_data
from .logging_config import logger

BASE_URL = "https://www.cnb.cz/en/financial_markets/foreign_exchange_market/exchange_rate_fixing/daily.txt"

def fetch_daily_exchange_rate(date_str):
    url = f"{BASE_URL}?date={date_str}"
    logger.info(f"Fetching exchange rates for date: {date_str}")
    response = requests.get(url)
    if response.status_code == 200:
        return parse_exchange_data(response.text)
    logger.error(f"Failed to fetch data for date {date_str}. Status code: {response.status_code}")
    return {}

def sync_daily_data():
    today = datetime.now().date()
    logger.info(f"Starting daily synchronization for date: {today}")
    data = fetch_daily_exchange_rate(today.strftime("%d.%m.%Y"))
    with next(get_db()) as db:
        for currency, rate in data.items():
            if currency in settings.currencies:
                existing_record = (
                    db.query(ExchangeRate)
                    .filter_by(date=today, currency=currency)
                    .first()
                )
                if existing_record:
                    logger.info(f"Updating record for {currency} on {today}")
                    existing_record.rate = rate
                else:
                    logger.info(f"Adding new record for {currency} on {today}")
                    db.add(ExchangeRate(date=today, currency=currency, rate=rate))
        db.commit()
    logger.info(f"Daily synchronization completed for date: {today}")

def sync_period_data(start_date, end_date):
    logger.info(f"Starting synchronization for period: {start_date} - {end_date}")
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    while current_date <= end:
        date_str = current_date.strftime("%d.%m.%Y")
        data = fetch_daily_exchange_rate(date_str)
        db_date = current_date.date()
        with next(get_db()) as db:
            for currency, rate in data.items():
                if currency in settings.currencies:
                    existing_record = (
                        db.query(ExchangeRate)
                        .filter_by(date=db_date, currency=currency)
                        .first()
                    )
                    if existing_record:
                        logger.info(f"Updating record for {currency} on {db_date}")
                        existing_record.rate = rate
                    else:
                        logger.info(f"Adding new record for {currency} on {db_date}")
                        db.add(ExchangeRate(date=db_date, currency=currency, rate=rate))
            db.commit()
        current_date += timedelta(days=1)
    logger.info(f"Synchronization completed for period: {start_date} - {end_date}")