import random
import math

# Быстрое возведение в степерь по модулю
def fast_pow(a, b, p):
    """Возвращает (a^b) mod p"""
    result = 1
    a = a % p
    while b > 0:
        if b % 2 == 1:  # Если степень нечетная
            result = (result * a) % p
        b = b >> 1      # Делим степень на 2 (сдвиг вправо)
        a = (a * a) % p
    return result

# Тест простоты Ферма
def fermat_test(n, k=5):
    """Проверяет число n на простоту с вероятностью 1 - (1/2)^k"""
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0: return False

    for _ in range(k):
        a = random.randint(2, n - 2)
        # Если a^(n-1) mod n != 1, то число точно составное
        if fast_pow(a, n - 1, n) != 1:
            return False
    return True

# Обобщенный алгоритм Евклида
def extended_gcd(a, b):
    """Возвращает (НОД, x, y) такие, что a*x + b*y = НОД"""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

# Генерация простых чисел
def generate_prime(bits=32):
    """Генерирует простое число заданной длины (в битах)"""
    while True:
        # Генерируем случайное нечетное число
        n = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        if fermat_test(n):
            return n

# Шаг великана, шаг младенца
def baby_step_giant_step(a, b, p):
    """
    Решает уравнение a^x = b (mod p).
    Возвращает x.
    """
    m = math.isqrt(p) + 1  # m = ceil(sqrt(p))
    
    # 1. Младенческие шаги (Baby steps)
    # Считаем b * a^j mod p и сохраняем в хеш-таблицу
    baby_steps = {}
    current_val = b % p
    for j in range(m):
        baby_steps[current_val] = j
        current_val = (current_val * a) % p
        
    # 2. Великанские шаги (Giant steps)
    # Считаем a^(m*i) mod p
    giant_step_base = fast_pow(a, m, p)
    current_val = 1
    for i in range(m):
        if current_val in baby_steps:
            j = baby_steps[current_val]
            x = i * m - j
            # Убеждаемся, что x положительный
            return x % (p - 1) 
        current_val = (current_val * giant_step_base) % p
        
    return None  # Если логарифм не найден

# Диффи-Хеллман
def diffie_hellman():
    # 1. Генерация или ввод открытых параметров
    p = generate_prime(32)
    g = random.randint(2, p - 2)
    print(f"Открытые параметры: p={p}, g={g}")

    # 2. Секретные ключи Алисы и Боба
    X_A = random.randint(2, p - 2)
    X_B = random.randint(2, p - 2)

    # 3. Открытые ключи (то, что они отправляют по каналу)
    Y_A = fast_pow(g, X_A, p)
    Y_B = fast_pow(g, X_B, p)
    print(f"Алиса отправила Бобу: {Y_A}")
    print(f"Боб отправил Алисе: {Y_B}")

    # 4. Вычисление общего секрета (K)
    # Алиса считает: K = Y_B ^ X_A mod p
    K_Alice = fast_pow(Y_B, X_A, p)
    # Боб считает: K = Y_A ^ X_B mod p
    K_Bob = fast_pow(Y_A, X_B, p)

    print(f"Секрет Алисы: {K_Alice}")
    print(f"Секрет Боба:  {K_Bob}")
    print(f"Ключи совпали? {K_Alice == K_Bob}")

# Получить инверсивный элемент
def get_inverse_element(e, phi):
    """Находит D такое, что (C * D) mod phi = 1. Использует расширенный Евклид."""
    gcd, x, y = extended_gcd(e, phi)
    if gcd != 1:
        raise ValueError("Обратного элемента не существует")
    return x % phi

# Шифр Шамира, шифрование
def shamir_encrypt_file(input_path, output_path, p, C):
    """Шифрует файл"""
    with open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
        while True:
            byte = f_in.read(1)
            if not byte: break
            
            M = byte[0]               # Читаем 1 байт (число 0-255)
            E = fast_pow(M, C, p)     # Шифруем: E = M^C mod p
            
            # Записываем как 8 байт (little-endian), чтобы число точно влезло
            f_out.write(E.to_bytes(8, byteorder='little'))

# Шифр Шамира, дешифрование
def shamir_decrypt_file(input_path, output_path, p, D):
    """Расшифровывает файл"""
    with open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
        while True:
            chunk = f_in.read(8)      # Читаем по 8 байт
            if not chunk: break
            
            E = int.from_bytes(chunk, byteorder='little')
            M = fast_pow(E, D, p)     # Расшифровываем: M = E^D mod p
            
            f_out.write(bytes([M]))   # Пишем обратно 1 байт