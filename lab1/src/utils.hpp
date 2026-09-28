#pragma once

struct EuclidResult
{
    long long g;
    long long x;
    long long y;
};

long long power_mod(long long a, long long x, long long p);
EuclidResult extended_gcd(long long a, long long b);
bool is_prime_fermat(long long p, int rounds);
long long random_number(long long lo, long long hi);
long long random_prime(long long lo, long long hi);
