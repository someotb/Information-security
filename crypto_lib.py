import random
import math
import hashlib
import json
import math
import secrets
from pathlib import Path

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

# Шифр Эль-Гамаля
def elgamal_generate_keys(bits=32):
    """Генерирует открытый и закрытый ключи Эль-Гамаля."""
    p = generate_prime(bits)
    g = random.randint(2, p - 2)
    x = secrets.randbelow(p - 2) + 1
    y = fast_pow(g, x, p)

    return {"p": p, "g": g, "x": x, "y": y}

def elgamal_encrypt_file(input_path, output_path, p, g, y):
    """Шифрует файл Эль-Гамалем, записывая пары чисел в бинарном виде."""
    width = (p.bit_length() + 7) // 8

    with open(input_path, "rb") as src, open(output_path, "wb") as dst:
        while True:
            byte = src.read(1)
            if not byte:
                break

            m = byte[0]
            k = secrets.randbelow(p - 2) + 1

            c1 = fast_pow(g, k, p)
            c2 = (m * fast_pow(y, k, p)) % p

            dst.write(c1.to_bytes(width, "big"))
            dst.write(c2.to_bytes(width, "big"))

def elgamal_decrypt_file(input_path, output_path, p, x):
    """Расшифровывает файл Эль-Гамаля."""
    width = (p.bit_length() + 7) // 8

    with open(input_path, "rb") as src, open(output_path, "wb") as dst:
        while True:
            block = src.read(2 * width)

            if not block:
                break

            if len(block) != 2 * width:
                raise ValueError("Повреждённый файл Эль-Гамаля")

            c1 = int.from_bytes(block[:width], "big")
            c2 = int.from_bytes(block[width:], "big")

            if not (0 < c1 < p and 0 <= c2 < p):
                raise ValueError("Некорректные данные шифротекста")

            shared = fast_pow(c1, x, p)
            inverse = get_inverse_element(shared, p)
            m = (c2 * inverse) % p

            if m > 255:
                raise ValueError("Некорректный расшифрованный байт")

            dst.write(bytes([m]))

# RSA для файлов
def rsa_generate_keys(bits=32):
    """Генерирует ключи RSA. bits — длина каждого простого числа."""
    while True:
        p = generate_prime(bits)
        q = generate_prime(bits)

        if p == q:
            continue

        n = p * q
        phi = (p - 1) * (q - 1)

        e = 65537

        if math.gcd(e, phi) != 1:
            e = 3

            while math.gcd(e, phi) != 1:
                e += 2

        d = get_inverse_element(e, phi)

        if n > 255:
            return {
                "p": p,
                "q": q,
                "n": n,
                "e": e,
                "d": d
            }

def rsa_encrypt_file(input_path, output_path, n, e):
    """Шифрует файл RSA побайтово."""
    width = (n.bit_length() + 7) // 8

    with open(input_path, "rb") as src, open(output_path, "wb") as dst:
        while True:
            byte = src.read(1)

            if not byte:
                break

            c = fast_pow(byte[0], e, n)
            dst.write(c.to_bytes(width, "big"))


def rsa_decrypt_file(input_path, output_path, n, d):
    """Расшифровывает файл RSA."""
    width = (n.bit_length() + 7) // 8

    with open(input_path, "rb") as src, open(output_path, "wb") as dst:
        while True:
            block = src.read(width)

            if not block:
                break

            if len(block) != width:
                raise ValueError("Повреждённый файл RSA")

            c = int.from_bytes(block, "big")

            if c >= n:
                raise ValueError("Некорректный блок RSA")

            m = fast_pow(c, d, n)

            if m > 255:
                raise ValueError("Некорректный расшифрованный байт")

            dst.write(bytes([m]))


# Диффи-Хеллман и шифр Вернама
def diffie_hellman_generate_params(bits=32):
    """
    Генерирует параметры Диффи-Хеллмана.
    Возвращает открытые параметры, секреты и общий ключ.
    """
    p = generate_prime(bits)
    g = random.randint(2, p - 2)

    x_a = secrets.randbelow(p - 2) + 1
    x_b = secrets.randbelow(p - 2) + 1

    y_a = fast_pow(g, x_a, p)
    y_b = fast_pow(g, x_b, p)

    k_a = fast_pow(y_b, x_a, p)
    k_b = fast_pow(y_a, x_b, p)

    if k_a != k_b:
        raise ArithmeticError("Ключи Диффи-Хеллмана не совпали")

    return {
        "p": p,
        "g": g,
        "x_a": x_a,
        "y_b": y_b,
        "shared_key": k_a
    }

def vernam_xor_file(input_path, output_path, shared_key):
    """
    Шифрует или расшифровывает файл операцией XOR.
    Поток ключа формируется из общего секрета Диффи-Хеллмана
    при помощи SHA-256 и счётчика блоков.
    """
    if shared_key < 0:
        raise ValueError("Ключ не может быть отрицательным")

    secret_bytes = shared_key.to_bytes(
        max(1, (shared_key.bit_length() + 7) // 8), "big"
    )

    counter = 0

    with open(input_path, "rb") as src, open(output_path, "wb") as dst:
        while True:
            data = src.read(65536)

            if not data:
                break

            stream = bytearray()

            while len(stream) < len(data):
                block = hashlib.sha256(
                    secret_bytes + counter.to_bytes(8, "big")
                ).digest()

                stream.extend(block)
                counter += 1

            result = bytes(
                a ^ b for a, b in zip(data, stream)
            )

            dst.write(result)


# Электронная подпись RSA

def rsa_sign_file(input_path, signature_path, n, d):
    """
    Подписывает SHA-256 файла.
    Каждый байт хеша подписывается отдельно, как допускает методичка.
    """
    with open(input_path, "rb") as src:
        digest = hashlib.sha256(src.read()).digest()

    if n <= 255:
        raise ValueError("Модуль RSA должен быть больше 255")

    signature = [
        fast_pow(byte, d, n)
        for byte in digest
    ]

    with open(signature_path, "w", encoding="utf-8") as dst:
        json.dump(signature, dst)


def rsa_verify_file(input_path, signature_path, n, e):
    """Проверяет электронную подпись RSA."""
    with open(input_path, "rb") as src:
        digest = hashlib.sha256(src.read()).digest()

    with open(signature_path, "r", encoding="utf-8") as src:
        signature = json.load(src)

    if not isinstance(signature, list) or len(signature) != 32:
        return False

    try:
        recovered = []

        for value in signature:
            if not isinstance(value, int) or not (0 <= value < n):
                return False

            byte = fast_pow(value, e, n)

            if byte > 255:
                return False

            recovered.append(byte)

        return secrets.compare_digest(bytes(recovered), digest)

    except (ValueError, TypeError, OverflowError):
        return False