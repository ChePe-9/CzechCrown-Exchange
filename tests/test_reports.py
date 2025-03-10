import pytest
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.models import ReportResponse
from app.api.reports import get_report
from datetime import datetime, date
import pytest_asyncio

# Создание тестовой базы данных в памяти
@pytest_asyncio.fixture(scope="function")
async def test_db():
    engine = create_engine("sqlite:///:memory:")  # Используем SQLite в памяти
    Base.metadata.create_all(engine)  # Создаем таблицы
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(engine)

# Фикстура для заполнения тестовых данных
@pytest_asyncio.fixture
async def seed_data(test_db):
    test_data = [
        {"date": datetime(2023, 10, 1).date(), "currency": "USD", "rate": 25.0},
        {"date": datetime(2023, 10, 1).date(), "currency": "EUR", "rate": 28.0},
        {"date": datetime(2023, 10, 2).date(), "currency": "USD", "rate": 26.0},
        {"date": datetime(2023, 10, 2).date(), "currency": "EUR", "rate": 29.0},
        {"date": datetime(2023, 10, 3).date(), "currency": "USD", "rate": 27.0},
        {"date": datetime(2023, 10, 3).date(), "currency": "EUR", "rate": 30.0},
    ]

    from app.database import ExchangeRate

    try:
        for data in test_data:
            test_db.add(ExchangeRate(date=data["date"], currency=data["currency"], rate=data["rate"]))
        test_db.commit()
    except Exception as e:
        test_db.rollback()
        raise e

# Тестирование логики формирования отчета
@pytest.mark.asyncio
async def test_get_report(test_db, seed_data):
    start_date = "2023-10-01"
    end_date = "2023-10-03"
    currencies = ["USD", "EUR"]

    report = await get_report(start_date, end_date, currencies, test_db)

    assert len(report) == 2  # Два элемента: USD и EUR
    usd_report = next(item for item in report if item.currency == "USD")
    assert usd_report.min_rate == 25.0
    assert usd_report.max_rate == 27.0
    assert usd_report.avg_rate == 26.0

    eur_report = next(item for item in report if item.currency == "EUR")
    assert eur_report.min_rate == 28.0
    assert eur_report.max_rate == 30.0
    assert eur_report.avg_rate == 29.0

# Тестирование ситуации, когда данных нет
@pytest.mark.asyncio
async def test_get_report_no_data(test_db):
    start_date = "2023-10-04"
    end_date = "2023-10-05"
    currencies = ["USD", "EUR"]

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        await get_report(start_date, end_date, currencies, test_db)

    assert exc_info.value.status_code == 404
    assert "No data found for" in str(exc_info.value.detail)

# Тестирование situations с одной валютой
@pytest.mark.asyncio
async def test_get_report_single_currency(test_db, seed_data):
    start_date = "2023-10-01"
    end_date = "2023-10-03"
    currencies = ["USD"]

    report = await get_report(start_date, end_date, currencies, test_db)

    assert len(report) == 1
    usd_report = report[0]
    assert usd_report.currency == "USD"
    assert usd_report.min_rate == 25.0
    assert usd_report.max_rate == 27.0
    assert usd_report.avg_rate == 26.0