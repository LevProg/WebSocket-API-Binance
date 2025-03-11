import asyncio
import websockets
import json
from ticker.models import TickerData
from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async

async def binance_websocket():
    uri = "wss://stream.binance.com:9443/ws/!ticker@arr"
    async with websockets.connect(uri) as websocket:
        # Словарь для хранения последних значений
        tickers = {
            "BTC/USDT": {"price": None, "volume": None},
            "ETH/USDT": {"price": None, "volume": None}
        }
        
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            for ticker in data:
                symbol = ticker['s']
                if symbol == "BTCUSDT":
                    tickers["BTC/USDT"]["price"] = float(ticker['c'])
                    tickers["BTC/USDT"]["volume"] = float(ticker['v'])
                elif symbol == "ETHUSDT":
                    tickers["ETH/USDT"]["price"] = float(ticker['c'])
                    tickers["ETH/USDT"]["volume"] = float(ticker['v'])

            await asyncio.sleep(60)

            for symbol, values in tickers.items():
                if values["price"] is not None and values["volume"] is not None:
                    await sync_to_async(TickerData.objects.create)(
                        symbol=symbol,
                        price=values["price"],
                        volume=values["volume"]
                    )
                    # Отправляем обновление через Channels
                    channel_layer = get_channel_layer()
                    await channel_layer.group_send(
                        "tickers",
                        {
                            "type": "send_ticker_update",
                            "data": {
                                "symbol": symbol,
                                "price": str(values["price"]),
                                "volume": str(values["volume"])
                            }
                        }
                    )

def start_websocket():
    asyncio.run(binance_websocket())