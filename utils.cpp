#include "utils.hpp"
#include <cstdlib>
#include <cmath>
#include <map>

EuclidResult extended_gcd(long long a, long long b)
{
    long long u1 = a, u2 = 1, u3 = 0;
    long long v1 = b, v2 = 0, v3 = 1;

    while (v1 != 0)
    {
        long long q = u1 / v1;
        long long t1 = u1 % v1;
        long long t2 = u2 - q * v2;
        long long t3 = u3 - q * v3;

        u1 = v1;
        u2 = v2;
        u3 = v3;
        v1 = t1;
        v2 = t2;
        v3 = t3;
    }
    return {u1, u2, u3};
}

long long power_mod(long long a, long long x, long long p)
{
    long long y = 1;
    a = a % p; // на случай, если a >= p
    while (x > 0)
    {
        if (x & 1) // проверка младшего бита x
            y = (y * a) % p;
        a = (a * a) % p; // возведение в квадрат
        x >>= 1;         // сдвигаем биты x вправо
    }
    return y;
}

bool is_prime_fermat(long long p, int rounds)
{
    if (p < 2)
        return false;
    if (p == 2 || p == 3)
        return true;

    for (int i = 0; i < rounds; i++)
    {
        long long a = rand() % (p - 3) + 2; // случайное a из [2, p-2]

        if (extended_gcd(a, p).g != 1)
            return false; // общий делитель: точно составное
        if (power_mod(a, p - 1, p) != 1)
            return false; // теорема Ферма нарушена: точно составное
    }
    return true; // ни одна проверка не поймала: вероятно простое
}

long long random_number(long long lo, long long hi)
{
    return lo + rand() % (hi - lo + 1);
}

long long random_prime(long long lo, long long hi)
{
    while (true)
    {
        long long c = random_number(lo, hi);
        if (is_prime_fermat(c, 100))
            return c;
    }
}

// Лабораторная работа №2: дискретный логарифм, "шаг младенца, шаг великана".

// Решает a^x = y (mod p), возвращает x или -1, если решения нет.
// Время: O(sqrt(p) * log(sqrt(p))) из-за std::map (поиск за log).
long long baby_giant(long long a, long long y, long long p)
{
    long long m = (long long)std::sqrt((double)p) + 1; // m*m > p
    a %= p;
    y %= p;

    // Шаги младенца: y * a^j mod p для j = 0..m-1
    std::map<long long, long long> baby;
    long long cur = y;
    for (long long j = 0; j < m; j++)
    {
        baby[cur] = j; // при повторах остаётся наибольшее j
        cur = (cur * a) % p;
    }

    // Шаги великана: a^(i*m) mod p для i = 1..m
    long long step = power_mod(a, m, p);
    cur = step;
    for (long long i = 1; i <= m; i++)
    {
        auto it = baby.find(cur);
        if (it != baby.end())
            return i * m - it->second; // x = i*m - j
        cur = (cur * step) % p;
    }
    return -1;
}

// Генерирует p (простое), a, секретный x и y = a^x mod p.
// Решение гарантированно существует, т.к. y построен из x.
bool generate_dlog_params(long long lo, long long hi,
                          long long &a, long long &y, long long &p,
                          long long &x_secret)
{
    p = random_prime(lo, hi);
    a = random_number(2, p - 2);
    x_secret = random_number(1, p - 2);
    y = power_mod(a, x_secret, p);
    return true;
}
