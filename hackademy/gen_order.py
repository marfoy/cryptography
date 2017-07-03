from random import randint
from sys import exit, argv
def is_prime(n):
	if(n <= 1):
		return (n,False)
	elif n <=3:
		return (n,True)
	elif n % 2 == 0 or n % 3 == 0:
		return (n,False)
	i = 5
	while(i*i <= n):
		if n % i == 0 or n % (i + 2) == 0:
			return (n,False)
		i = i + 6
	return (n,True)

def pow_mod(a, k, n):
	y = 1
	z = a
	l = k
	while l > 0:
		r = l & 1
		q = l >> 1
		if r:
			y = (y * z) % n
		z = (z * z) % n
		l = q
	return y

def fermat(n,i=10):
	for _ in range(i):
		a = randint(2,n)
		if pow_mod(a,n,n) != a:
			return False
	return True

if __name__ == "__main__":
	#f = open("equaLin/n_ponp",'r')
	#n = int(f.read())
	#f.close()
	f = open("q_gen",'r')
	q = int(f.read())
	f.close()
	f = open(argv[1],'r')
	a = int(f.read())
	f.close()
	f = open(argv[2],'r')
	b = int(f.read())
	f.close()
	q = 93691377971125351205639587584357289543841454536490973778030662552847384667119
	while 1:
		x = randint(a/q,b/q)
		p = x*q + 1
		if fermat(p):
			print("P:::::\n")
			print(p)
			break

	g = 1
	while g == 1:
		x = randint(2,2**64)
		g = pow_mod(x,((p-1) // q),p)
	print("G:::::\n")
	print(g)
