import os
import io
import pytest
from app import app as flask_app


@pytest.fixture()
def app():
    # Configure app for testing
    flask_app.config.update({
        "TESTING": True,
    })
    yield flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def tiny_valid_csv_bytes():
    # More realistic CSV with enough data for analytics to work
    # Matches the structure of real order data files
    content = (
        "Order ID,Timestamp,Fill Time,B/S,Contract,filledQty,Avg Fill Price,Type,Limit Price,Stop Price,Status\n"
        "7301604731,01/02/2024 7:30:00,01/02/2024 7:30:00,Buy,MNQH4,1,21490.25,Market,21490.25,,Filled\n"
        "7301604733,01/02/2024 7:30:00,01/02/2024 7:36:47,Sell,MNQH4,1,21505.25,Limit,21505.25,,Filled\n"
        "7301604621,01/02/2024 8:11:05,01/02/2024 8:11:05,Buy,MNQH4,1,21461.25,Market,21461.25,,Filled\n"
        "7301604623,01/02/2024 8:11:05,01/02/2024 8:12:05,Sell,MNQH4,1,21481.5,Limit,21481.5,,Filled\n"
        "7301602951,01/02/2024 9:12:12,01/02/2024 9:12:12,Sell,MNQH4,1,21523,Market,21523,,Filled\n"
        "7301602953,01/02/2024 9:12:12,01/02/2024 9:18:18,Buy,MNQH4,1,21507.25,Limit,21507.25,,Filled\n"
    )
    return content.encode("utf-8")


def make_file_storage(name: str, data: bytes):
    return (io.BytesIO(data), name)
