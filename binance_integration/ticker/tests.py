import pytest
import json
import asyncio
from unittest.mock import patch, AsyncMock
from django.test import TestCase
from rest_framework.test import APIClient
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from ticker.models import TickerData
from ticker.consumers import TickerConsumer
from ticker.websocket_client import binance_websocket
from binance_integration.asgi import application
from decimal import Decimal
from asgiref.sync import sync_to_async

# Тесты для модели
class TickerDataModelTest(TestCase):
    def test_ticker_data_creation(self):
        ticker = TickerData.objects.create(
            symbol="BTC/USDT",
            price=Decimal("50000.1234567890"),
            volume=Decimal("1.5")
        )
        self.assertEqual(ticker.symbol, "BTC/USDT")
        self.assertEqual(ticker.price, Decimal("50000.1234567890"))
        self.assertTrue(ticker.timestamp)

    def test_string_representation(self):
        ticker = TickerData.objects.create(symbol="ETH/USDT", price=2000, volume=2.0)
        self.assertEqual(str(ticker), "ETH/USDT - 2000")

# Тесты для REST API
@pytest.mark.django_db
def test_ticker_data_api():
    client = APIClient()
    TickerData.objects.create(symbol="BTC/USDT", price=Decimal("50000"), volume=Decimal("1.5"))
    TickerData.objects.create(symbol="ETH/USDT", price=Decimal("2000"), volume=Decimal("2.0"))

    response = client.get('/api/ticker-data/')
    assert response.status_code == 200
    assert len(response.json()) == 2
    symbols = [item["symbol"] for item in response.json()]
    assert "BTC/USDT" in symbols
    assert "ETH/USDT" in symbols

@pytest.mark.django_db
def test_ticker_data_api_filter():
    client = APIClient()
    TickerData.objects.create(symbol="BTC/USDT", price=Decimal("50000"), volume=Decimal("1.5"))
    TickerData.objects.create(symbol="ETH/USDT", price=Decimal("2000"), volume=Decimal("2.0"))

    response = client.get('/api/ticker-data/?symbol=BTC/USDT')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["symbol"] == "BTC/USDT"

# Тесты для WebSocket Consumer
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_ticker_consumer():
    communicator = WebsocketCommunicator(application, "/ws/tickers/")
    connected, subprotocol = await communicator.connect()
    assert connected

    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        "tickers",
        {
            "type": "send_ticker_update",
            "data": {"symbol": "BTC/USDT", "price": "50000", "volume": "1.5"}
        }
    )
    response = await communicator.receive_json_from(timeout=2)
    assert response == {"symbol": "BTC/USDT", "price": "50000", "volume": "1.5"}

    await communicator.disconnect()

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_binance_websocket():
    with patch('ticker.websocket_client.websockets.connect', new_callable=AsyncMock) as mock_connect:
        mock_websocket = AsyncMock()
        mock_websocket.recv.side_effect = [
            json.dumps([
                {"s": "BTCUSDT", "c": "50000", "v": "1.5"},
                {"s": "ETHUSDT", "c": "2000", "v": "2.0"}
            ]),
            asyncio.CancelledError()
        ]
        mock_connect.return_value.__aenter__.return_value = mock_websocket
        mock_connect.return_value.__aexit__.return_value = None

        with patch('asyncio.sleep', return_value=asyncio.sleep(0)):
            with patch('channels.layers.get_channel_layer', return_value=AsyncMock()) as mock_channel_layer:
                task = asyncio.create_task(binance_websocket())
                await asyncio.sleep(0.1) 
                task.cancel()

                count = await sync_to_async(TickerData.objects.count)()
                assert count == 2, f"Expected 2 records, got {count}"
                btc_data = await sync_to_async(TickerData.objects.get)(symbol="BTC/USDT")
                eth_data = await sync_to_async(TickerData.objects.get)(symbol="ETH/USDT")
                assert btc_data.price == Decimal("50000")
                assert eth_data.price == Decimal("2000")
        
@pytest.mark.asyncio
async def test_binance_websocket_connection_error():
    with patch('ticker.websocket_client.websockets.connect', side_effect=Exception("Connection failed")):
        with pytest.raises(Exception, match="Connection failed"):
            await binance_websocket()