import numpy
import scipy
import sys


def lcm(x1, x2):
    if (x1 > x2):
        greater = x1
    else:
        greater = x2
    while (True):
        if ((greater % x1 == 0) and (greater % x2 == 0)):
            lcm = greater
            break
        greater += 1
    return lcm


def L(x, n):
    return (x - 1) / n


def egcd(a, b):
    if a == 0:
        return b, 0, 1
    else:
        g, x, y = egcd(b % a, a)
        return g, y - (b // a) * x, x


def mulinv(b, n):
    g, x, _ = egcd(b, n)
    if g == 1:
        return x % n


def m(c, g, lambd, n):
    L1 = L(pow(c, lambd, n ** 2), n)
    L2 = L(pow(g, lambd, n ** 2), n)
    L2inv = mulinv(L2, n)
    m = (L1 * L2inv) % n
    print "m", m
    return m


def voters(vtot):
    if vtot > len(cvec):
        return vtot-n
    else:
        return vtot


p = 1117
q = 1471
g = 652534095028
n = p * q
cvec = []
ctot = 1
card_file = open('votes.txt', 'r')
for i in card_file:
    cvec.append(int(i.strip('\n')))
for i in cvec:
    ctot = ctot * i
ctot = ctot % (n**2)
lambd = lcm(p - 1, q - 1)
print voters(m(ctot, g, lambd, n))
