from crypto_lib import extended_gcd, generate_prime

def main():
    mode = input("Выберите режим (1 - ввод с клавиатуры, 2 - генерация): ")
    
    if mode == '1':
        a = int(input("Введите a: "))
        b = int(input("Введите b: "))
    else:
        # Генерация простых чисел внутри функции (как требует задание)
        a = generate_prime(32)
        b = generate_prime(32)
        print(f"Сгенерированы простые числа: a={a}, b={b}")

    # Вызов функции из библиотеки
    gcd, x, y = extended_gcd(a, b)
    print(f"Результат: НОД={gcd}, x={x}, y={y}")

if __name__ == "__main__":
    main()