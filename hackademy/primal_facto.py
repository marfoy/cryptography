from primal_test import *
from random import randint, seed
from equaLin.inv_mod import load_int

def prime_prod(a,b):
	acc = 1
	p_l = []
	while acc < a/2**24:
		x = randint(2,2**64-1)
		if fermat(x):
			acc*=x
			p_l.append(x)
	acc/= x
	p_l.remove(x)
	n_a = a/acc
	n_b = b/acc
	for n in range(max(n_a,2),max(3,n_b+1)):
		if fermat(n) and fermat(n+1) and acc*(n+1) >= a and acc*(n+1) <= b:
			acc*= n
			p_l.append(n)
			return acc, p_l
	return None,None

a = load_int("a_plus")
b = load_int("b_plus")
n, factors = prime_prod(a,b)
while n == None:
	n, factors = prime_prod(a,b)
print("["+",".join(map(str, factors))+"]")
