from crypto_lib import baby_step_giant_step, fast_pow, generate_prime

def main():
    mode = input("Выберите режим (1 - ввод с клавиатуры, 2 - генерация): ")
    
    if mode == '1':
        a = int(input("Введите a: "))
        y = int(input("Введите y: "))
        p = int(input("Введите p: "))
    else:
        p = generate_prime(32)
        a = 5 # или сгенерить случайное
        x_true = 12345
        y = fast_pow(a, x_true, p)
        print(f"Сгенерировано: a={a}, p={p}, y={y}")

    x = baby_step_giant_step(a, y, p)
    print(f"Найденный дискретный логарифм x = {x}")

if __name__ == "__main__":
    main()