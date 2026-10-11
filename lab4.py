from crypto_lib import generate_prime, get_inverse_element, shamir_encrypt_file, shamir_decrypt_file
import math
import os

def main():
    mode = input("Выберите режим (1 - ввод с клавиатуры, 2 - генерация): ")
    
    if mode == '1':
        p = int(input("Введите простое p: "))
        C = int(input("Введите открытый ключ C: "))
    else:
        # Генерация ключей внутри функции
        p = generate_prime(32)
        phi = p - 1
        
        # Ищем C (открытый ключ), взаимно простой с phi
        while True:
            C = random.randint(2, phi - 1)
            if math.gcd(C, phi) == 1:
                break
        
        print(f"Сгенерировано: p={p}, открытый ключ C={C}")

    # Вычисляем закрытый ключ D
    D = get_inverse_element(C, p - 1)
    print(f"Закрытый ключ D = {D}")
    
    # Выбор действия
    action = input("\nЧто сделать? (1 - зашифровать, 2 - расшифровать): ")
    
    if action == '1':
        input_file = input("Введите путь к файлу для шифрования: ")
        output_file = input("Введите путь для сохранения зашифрованного файла: ")
        shamir_encrypt_file(input_file, output_file, p, C)
        print(f"Файл зашифрован в {output_file}")
        
    elif action == '2':
        input_file = input("Введите путь к зашифрованному файлу: ")
        output_file = input("Введите путь для сохранения расшифрованного файла: ")
        shamir_decrypt_file(input_file, output_file, p, D)
        print(f"Файл расшифрован в {output_file}")
    else:
        print("Неверный выбор")

if __name__ == "__main__":
    import random  # Нужно для генерации C
    main()