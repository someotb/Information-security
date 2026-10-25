import json
from pathlib import Path

from crypto_lib import (
    elgamal_generate_keys,
    elgamal_encrypt_file,
    elgamal_decrypt_file
)

KEY_FILE = "elgamal_key.json"


def main():
    print("Лабораторная работа №5 — Эль-Гамаль")
    print("1. Зашифровать файл")
    print("2. Расшифровать файл")

    choice = input("Выберите действие: ").strip()

    if choice == "1":
        input_path = input("Исходный файл: ").strip()
        output_path = input("Файл для шифротекста: ").strip()

        if Path(input_path).resolve() == Path(output_path).resolve():
            raise ValueError("Входной и выходной файлы должны различаться")

        keys = elgamal_generate_keys()

        elgamal_encrypt_file(
            input_path, output_path,
            keys["p"], keys["g"], keys["y"]
        )

        with open(KEY_FILE, "w", encoding="utf-8") as f:
            json.dump(keys, f)

        print("Файл зашифрован.")
        print(f"Ключ сохранён в {KEY_FILE}")

    elif choice == "2":
        input_path = input("Файл с шифротекстом: ").strip()
        output_path = input("Файл для результата: ").strip()

        if Path(input_path).resolve() == Path(output_path).resolve():
            raise ValueError("Входной и выходной файлы должны различаться")

        with open(KEY_FILE, "r", encoding="utf-8") as f:
            keys = json.load(f)

        elgamal_decrypt_file(
            input_path, output_path,
            keys["p"], keys["x"]
        )

        print("Файл расшифрован.")

    else:
        print("Неизвестный пункт меню.")


if __name__ == "__main__":
    main()