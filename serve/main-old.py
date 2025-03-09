import asyncio
import websockets
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Множество для хранения активных WebSocket-подключений
connected_clients = set()

async def handle_connection(websocket):
    """
    Обработчик нового подключения.
    Регистрирует клиента, принимает входящие сообщения и транслирует их всем подключенным клиентам.
    """
    connected_clients.add(websocket)
    logger.info(f"Новое подключение: {websocket.remote_address}")
    try:
        async for message in websocket:
            logger.info(f"Получено сообщение: {message} от {websocket.remote_address}")
            await broadcast(message)
    except websockets.exceptions.ConnectionClosed as e:
        logger.warning(f"Соединение с клиентом {websocket.remote_address} закрыто: {e}")
    finally:
        connected_clients.remove(websocket)
        logger.info(f"Клиент {websocket.remote_address} отключился")

async def broadcast(message):
    """
    Транслирует полученное сообщение всем подключенным клиентам.
    """
    if connected_clients:
        # Отправляем сообщение всем клиентам, используя asyncio.gather
        await asyncio.gather(*(client.send(message) for client in connected_clients))

async def main():
    # Запуск WebSocket-сервера на localhost:8765
    server = await websockets.serve(handle_connection, "localhost", 8765) # websockets.serve(handle_connection, "0.0.0.0", 8765)
    logger.info("WebSocket сервер запущен на ws://localhost:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())


# pip install websockets
# Запуск сервера: python .\serve\main.py &
# Запуск клиента: cd client/ && python -m http.server 8000 &