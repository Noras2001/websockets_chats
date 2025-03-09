## **Домашнее задание**

### Добавьте функционал сохранения истории сообщений

##### - Организуйте хранение сообщений в памяти или в текстовом файле (например, chat_history.txt), чтобы при перезапуске сервера история не терялась.
##### - Реализуйте логику загрузки и отправки последних N сообщений (например, 10 или 20) новому пользователю при подключении.

import asyncio
import websockets
import logging
import os

# Файл для хранения истории сообщений
CHAT_HISTORY_FILE = "chat_history.txt"
MAX_HISTORY_MESSAGES = 20  # Количество последних сообщений для отправки новым пользователям

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Множество для хранения активных WebSocket-подключений
connected_clients = set()

async def load_chat_history():
    """
    Загружает последние N сообщений из файла истории.
    """
    if not os.path.exists(CHAT_HISTORY_FILE):
        return []

    with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as file:
        messages = file.readlines()
    
    return messages[-MAX_HISTORY_MESSAGES:]  # Берём последние N сообщений


async def save_message_to_history(message):
    """
    Сохраняет сообщение в файл истории.
    """
    with open(CHAT_HISTORY_FILE, "a", encoding="utf-8") as file:
        file.write(message + "\n")


async def handle_connection(websocket):
    """
    Обработчик нового подключения.
    Регистрирует клиента, отправляет историю сообщений и принимает входящие сообщения.
    """
    connected_clients.add(websocket)
    logger.info(f"Новое подключение: {websocket.remote_address}")

    try:
        # Отправка истории сообщений новому пользователю
        chat_history = await load_chat_history()
        for msg in chat_history:
            await websocket.send(msg.strip())  # strip() убирает лишние переводы строк
        
        # Приём сообщений от пользователя
        async for message in websocket:
            logger.info(f"Получено сообщение: {message} от {websocket.remote_address}")
            
            # Сохраняем сообщение в историю
            await save_message_to_history(message)
            
            # Транслируем сообщение всем подключенным клиентам
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
        await asyncio.gather(*(client.send(message) for client in connected_clients))


async def main():
    """
    Запускает WebSocket-сервер на ws://localhost:8765.
    """
    server = await websockets.serve(handle_connection, "localhost", 8765)
    logger.info("WebSocket сервер запущен на ws://localhost:8765")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())


# pip install websockets
# Запуск сервера: python .\serve\main.py &
# Запуск клиента: cd client/ && python -m http.server 8000 &