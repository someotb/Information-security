import json
from pathlib import Path

from crypto_lib import (
    elgamal_signature_generate_keys,
    elgamal_sign_file,
    elgamal_verify_file
)

KEY_FILE = "elgamal_signature_keys.json"
SIGNATURE_FILE = "elgamal_signature.json"


def main():
    print("Лабораторная работа №9 — Подпись Эль-Гамаля")
    print("1. Подписать файл")
    print("2. Проверить подпись")

    choice = input("Выберите действие: ").strip()

    if choice == "1":
        input_path = input("Исходный файл: ").strip()
        signature_path = input(
            f"Файл подписи [{SIGNATURE_FILE}]: "
        ).strip() or SIGNATURE_FILE

        if Path(input_path).resolve() == Path(signature_path).resolve():
            raise ValueError("Файл подписи не должен заменять исходный файл")

        keys = elgamal_signature_generate_keys()

        elgamal_sign_file(
            input_path,
            signature_path,
            keys["p"],
            keys["g"],
            keys["x"]
        )

        with open(KEY_FILE, "w", encoding="utf-8") as f:
            json.dump(keys, f)

        print("Подпись создана.")
        print(f"Подпись: {signature_path}")
        print(f"Ключи: {KEY_FILE}")

    elif choice == "2":
        input_path = input("Файл для проверки: ").strip()
        signature_path = input(
            f"Файл подписи [{SIGNATURE_FILE}]: "
        ).strip() or SIGNATURE_FILE

        with open(KEY_FILE, "r", encoding="utf-8") as f:
            keys = json.load(f)

        valid = elgamal_verify_file(
            input_path,
            signature_path,
            keys["p"],
            keys["g"],
            keys["y"]
        )

        print(
            "Подпись корректна."
            if valid else
            "Подпись НЕ корректна."
        )

    else:
        print("Неизвестный пункт меню.")


if __name__ == "__main__":
    main()