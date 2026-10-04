#include "../../utils.hpp"
#include <cstdlib>
#include <ctime>
#include <iostream>

void run_power_mod()
{
    long long a, x, p;
    std::cout << "Введите a, x, p (считаем a^x mod p): ";
    std::cin >> a >> x >> p;
    if (p <= 0 || x < 0)
    {
        std::cout << "Нужно p > 0 и x >= 0\n";
        return;
    }
    std::cout << a << "^" << x << " mod " << p << " = " << power_mod(a, x, p) << "\n";
}

void run_fermat()
{
    long long p;
    std::cout << "Введите число для проверки на простоту: ";
    std::cin >> p;
    if (is_prime_fermat(p, 100))
        std::cout << p << " - вероятно простое\n";
    else
        std::cout << p << " - точно составное\n";
}

void run_euclid()
{
    std::cout << "1 - ввод a, b с клавиатуры\n"
                 "2 - случайные a, b\n"
                 "3 - случайные простые a, b\n";
    int mode;
    std::cin >> mode;

    long long a, b;
    if (mode == 1)
        std::cin >> a >> b;
    else if (mode == 2)
    {
        a = random_number(1, 1000000000);
        b = random_number(1, 1000000000);
    }
    else
    {
        a = random_prime(2, 1000000000);
        b = random_prime(2, 1000000000);
    }

    EuclidResult r = extended_gcd(a, b);
    std::cout << "a = " << a << ", b = " << b << "\n"
              << "НОД = " << r.g << ", x = " << r.x << ", y = " << r.y << "\n"
              << a << "*(" << r.x << ") + " << b << "*(" << r.y << ") = " << a * r.x + b * r.y << "\n";
}

int main()
{
    srand(time(nullptr));

    while (true)
    {
        std::cout << "\n1 - быстрое возведение в степень по модулю\n"
                     "2 - тест простоты Ферма\n"
                     "3 - обобщённый алгоритм Евклида\n"
                     "0 - выход\n";
        int task;
        std::cin >> task;

        if (task == 1)
            run_power_mod();
        else if (task == 2)
            run_fermat();
        else if (task == 3)
            run_euclid();
        else
            break;
    }
}
