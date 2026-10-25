import json
from pathlib import Path

from crypto_lib import (
    rsa_generate_keys,
    rsa_sign_file,
    rsa_verify_file
)

KEY_FILE = "rsa_signature_keys.json"
SIGNATURE_FILE = "signature.json"


def main():
    print("Лабораторная работа №8 — Электронная подпись RSA")
    print("1. Подписать файл")
    print("2. Проверить подпись")

    choice = input("Выберите действие: ").strip()

    if choice == "1":
        input_path = input("Файл для подписания: ").strip()
        signature_path = input(
            f"Файл подписи [{SIGNATURE_FILE}]: "
        ).strip() or SIGNATURE_FILE

        if Path(input_path).resolve() == Path(signature_path).resolve():
            raise ValueError("Файл подписи не должен заменять исходный файл")

        keys = rsa_generate_keys()

        rsa_sign_file(
            input_path, signature_path, keys["n"], keys["d"]
        )

        # Закрытый ключ нужен для подписания, открытый — для проверки.
        with open(KEY_FILE, "w", encoding="utf-8") as f:
            json.dump(keys, f)

        print("Подпись создана.")
        print(f"Подпись: {signature_path}")
        print(f"Параметры ключа: {KEY_FILE}")

    elif choice == "2":
        input_path = input("Файл для проверки: ").strip()
        signature_path = input(
            f"Файл подписи [{SIGNATURE_FILE}]: "
        ).strip() or SIGNATURE_FILE

        with open(KEY_FILE, "r", encoding="utf-8") as f:
            keys = json.load(f)

        valid = rsa_verify_file(
            input_path, signature_path, keys["n"], keys["e"]
        )

        if valid:
            print("Подпись корректна. Файл не изменён.")
        else:
            print("Подпись НЕ корректна: файл изменён "
                  "или подпись повреждена.")

    else:
        print("Неизвестный пункт меню.")


if __name__ == "__main__":
    main()