import json
from pathlib import Path

from crypto_lib import (
    diffie_hellman_generate_params,
    fast_pow,
    vernam_xor_file
)

KEY_FILE = "vernam_key.json"


def main():
    print("Лабораторная работа №7 — Вернам")
    print("1. Зашифровать файл")
    print("2. Расшифровать файл")

    choice = input("Выберите действие: ").strip()

    if choice == "1":
        input_path = input("Исходный файл: ").strip()
        output_path = input("Файл для шифротекста: ").strip()

        if Path(input_path).resolve() == Path(output_path).resolve():
            raise ValueError("Входной и выходной файлы должны различаться")

        params = diffie_hellman_generate_params()
        shared_key = params["shared_key"]

        print(f"p = {params['p']}")
        print(f"g = {params['g']}")
        print(f"Открытый ключ Алисы = "
              f"{fast_pow(params['g'], params['x_a'], params['p'])}")
        print(f"Открытый ключ Боба = {params['y_b']}")
        print(f"Общий ключ = {shared_key}")

        vernam_xor_file(input_path, output_path, shared_key)

        # Сохраняем параметры для повторного получения общего ключа.
        saved_params = {
            "p": params["p"],
            "g": params["g"],
            "x_a": params["x_a"],
            "y_b": params["y_b"]
        }

        with open(KEY_FILE, "w", encoding="utf-8") as f:
            json.dump(saved_params, f)

        print("Файл зашифрован.")
        print(f"Параметры сохранены в {KEY_FILE}")

    elif choice == "2":
        input_path = input("Файл с шифротекстом: ").strip()
        output_path = input("Файл для результата: ").strip()

        if Path(input_path).resolve() == Path(output_path).resolve():
            raise ValueError("Входной и выходной файлы должны различаться")

        with open(KEY_FILE, "r", encoding="utf-8") as f:
            params = json.load(f)

        shared_key = fast_pow(
            params["y_b"], params["x_a"], params["p"]
        )

        vernam_xor_file(input_path, output_path, shared_key)

        print("Файл расшифрован.")

    else:
        print("Неизвестный пункт меню.")


if __name__ == "__main__":
    main()