#include "../../utils.hpp"
#include <iostream>

int main()
{
    std::cout << "1 - ввод a, y, p с клавиатуры\n2 - генерация параметров\n> ";
    int mode;
    std::cin >> mode;

    long long a, y, p, x_secret = -1;
    if (mode == 1)
    {
        std::cout << "a y p: ";
        std::cin >> a >> y >> p;
        if (p < 3 || !is_prime_fermat(p, 100))
            std::cout << "Предупреждение: p не похоже на простое, результат не гарантирован\n";
    }
    else
    {
        long long lo, hi;
        std::cout << "Границы для p (lo hi): ";
        std::cin >> lo >> hi;
        generate_dlog_params(lo, hi, a, y, p, x_secret);
        std::cout << "a=" << a << " y=" << y << " p=" << p
                  << " (загаданный x=" << x_secret << ")\n";
    }

    long long x = baby_giant(a, y, p);
    if (x == -1)
        std::cout << "Решения нет\n";
    else
        std::cout << "x = " << x << ", проверка a^x mod p = " << power_mod(a, x, p)
                  << " (ожидалось " << y % p << ")\n";
}