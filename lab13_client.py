import argparse
import math
import secrets

from lab13_common import DEFAULT_HOST, DEFAULT_PORT, send_request


CHOICES = {
    "1": ("Да", 0),
    "2": ("Нет", 1),
    "3": ("Воздержался", 2),
}


def main():
    parser = argparse.ArgumentParser(
        description="Клиент лабораторной работы №13 — анонимное голосование."
    )
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    print("Анонимное голосование со слепой RSA-подписью")
    voter_id = input("Введите идентификатор избирателя: ").strip()
    if not voter_id:
        print("Идентификатор не может быть пустым.")
        return

    print("\nВарианты ответа:")
    print("1 — Да")
    print("2 — Нет")
    print("3 — Воздержался")
    selected = input("Ваш выбор: ").strip()

    if selected not in CHOICES:
        print("Неизвестный вариант ответа.")
        return

    choice_name, choice_code = CHOICES[selected]

    try:
        # Получаем открытый RSA-ключ сервера.
        public = send_request(
            args.host, args.port, {"action": "public_key"}
        )
        n = public["n"]
        e = public["e"]

        # Кодируем выбор вместе со случайным номером бюллетеня:
        # m = nonce * 3 + choice_code.
        # Сервер не может определить choice_code из ослеплённого сообщения.
        nonce_limit = (n - 1) // 3
        if nonce_limit < 2:
            raise RuntimeError("Модуль RSA слишком мал для формирования бюллетеня.")

        nonce = secrets.randbelow(nonce_limit - 1) + 1
        message = nonce * 3 + choice_code

        # Выбираем r, взаимно простой с n.
        while True:
            r = secrets.randbelow(n - 1) + 1
            if math.gcd(r, n) == 1:
                break

        # Ослепление: m' = m * r^e mod n.
        r_power = pow(r, e, n)
        blinded_message = (message * r_power) % n

        print("\nПараметры и промежуточные значения:")
        print(f"n = {n}")
        print(f"e = {e}")
        print(f"Исходное сообщение m = {message}")
        print(f"Случайный множитель r = {r}")
        print(f"r^e mod n = {r_power}")
        print(f"Ослеплённое сообщение m' = {blinded_message}")

        # Передаём серверу только идентификатор и ослеплённое сообщение.
        signed = send_request(
            args.host,
            args.port,
            {
                "action": "blind_sign",
                "voter_id": voter_id,
                "blinded_message": blinded_message,
            },
        )
        blinded_signature = signed["blinded_signature"]
        print(f"Слепая подпись сервера s' = {blinded_signature}")

        # Снимаем ослепление: s = s' * r^(-1) mod n.
        r_inverse = pow(r, -1, n)
        signature = (blinded_signature * r_inverse) % n
        print(f"Обратный элемент r^(-1) mod n = {r_inverse}")
        print(f"Обычная подпись s = {signature}")

        # Локально проверяем подпись перед отправкой бюллетеня.
        local_check = pow(signature, e, n)
        print(f"Проверка s^e mod n = {local_check}")

        if local_check != message:
            raise RuntimeError("Локальная проверка подписи не пройдена.")

        # Отправляем бюллетень без voter_id.
        # Сервер проверяет подпись и принимает сообщение только один раз.
        accepted = send_request(
            args.host,
            args.port,
            {
                "action": "submit_ballot",
                "message": message,
                "signature": signature,
            },
        )

        print(f"\nГолос «{choice_name}» принят сервером.")
        print("Идентификатор избирателя при отправке бюллетеня не передавался.")
        print(f"Ответ сервера: {accepted['choice']}")

        results = send_request(args.host, args.port, {"action": "results"})
        print("\nТекущие результаты:")
        for name, count in results["counts"].items():
            print(f"{name}: {count}")
        print(f"Всего голосов: {results['total']}")

    except (OSError, ValueError, RuntimeError, KeyError) as error:
        print(f"\nОшибка: {error}")


if __name__ == "__main__":
    main()
