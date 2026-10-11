from crypto_lib import generate_prime, fast_pow
import random

def main():
    mode = input("Выберите режим (1 - ввод с клавиатуры, 2 - генерация): ")
    
    if mode == '1':
        p = int(input("Введите простое p: "))
        g = int(input("Введите g (основание): "))
        X_A = int(input("Введите секретный ключ Алисы X_A: "))
        X_B = int(input("Введите секретный ключ Боба X_B: "))
    else:
        # Генерация параметров внутри функции
        p = generate_prime(32)
        g = random.randint(2, p - 2)
        X_A = random.randint(2, p - 2)
        X_B = random.randint(2, p - 2)
        print(f"Сгенерировано: p={p}, g={g}")
        print(f"Секрет Алисы X_A={X_A}, секрет Боба X_B={X_B}")

    # Вычисление открытых ключей (то, что отправляется по каналу)
    Y_A = fast_pow(g, X_A, p)
    Y_B = fast_pow(g, X_B, p)
    print(f"\nОткрытый ключ Алисы Y_A = {Y_A}")
    print(f"Открытый ключ Боба Y_B = {Y_B}")

    # Вычисление общего секретного ключа
    K_Alice = fast_pow(Y_B, X_A, p)  # Алиса считает: Y_B ^ X_A mod p
    K_Bob = fast_pow(Y_A, X_B, p)    # Боб считает: Y_A ^ X_B mod p

    print(f"\nСекрет Алисы: K = {K_Alice}")
    print(f"Секрет Боба:  K = {K_Bob}")
    
    if K_Alice == K_Bob:
        print("Ключи совпали! Общий секрет успешно выработан.")
    else:
        print("ОШИБКА: Ключи не совпали!")

if __name__ == "__main__":
    main()