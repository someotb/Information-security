#include "utils.hpp"

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
