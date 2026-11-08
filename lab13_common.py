"""Общие функции лабораторной работы №13."""

import json
import socket


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5050


def send_request(host, port, data):
    """Отправляет один JSON-запрос и получает один JSON-ответ."""
    payload = json.dumps(data).encode("utf-8") + b"\n"

    with socket.create_connection((host, port), timeout=10) as sock:
        sock.sendall(payload)
        file = sock.makefile("rb")
        response = file.readline()

    if not response:
        raise ConnectionError("Сервер закрыл соединение без ответа.")

    result = json.loads(response.decode("utf-8"))
    if not result.get("ok", False):
        raise RuntimeError(result.get("error", "Неизвестная ошибка сервера."))

    return result
