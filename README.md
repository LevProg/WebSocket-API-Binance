# WebSocket-API-Binance
Тестовое задание. Интеграция с WebSocket API Задача: Реализовать Django-приложение с WebSocket-интеграцией к публичному API Binance.

Требования к API:
1. Подключиться к WebSocket API Binance (Tickers Stream).
2. Получать обновления цен по выбранным криптовалютным парам (например, BTC/USDT, ETH/USDT).
3. Сохранять обновленные данные в PostgreSQL.
4. Предоставить REST API для просмотра истории изменений.
5. Реализовать WebSocket-сервер в Django (Django Channels),
- который рассылает обновления клиентам в реальном времени.
6. Unit-тесты.
