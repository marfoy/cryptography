from primal_test import *
from random import randint, seed
from equaLin.inv_mod import load_int

def prime_prod(a,b):
	acc = 1
	p_l = []
	while acc < a:
		x = randint(1,2**64-1)
		if fermat(x):
			acc*=x
			p_l.append(x)
	acc/= x
	p_l.remove(x)
	n_a = a/acc
	n_b = b/acc
	for n in range(n_a,n_b+1):
		if fermat(n) and acc*n >= a and acc*n <= b:
			acc*= n
			p_l.append(n)
			return acc, p_l
	return None,None

a = load_int("a")
b = load_int("b")
n, factors = prime_prod(a,b)
while n == None:
	n, factors = prime_prod(a,b)
print("["+",".join(map(str, factors))+"]")
