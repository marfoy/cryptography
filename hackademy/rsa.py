from primal_test import *
import math
import time
from random import randint, seed
from equaLin.inv_mod import *

e = 126017296099303191660925274856916404887
def crypt_rsa():
	T = 2**1024
	p = randint(0,T) | T
	q = randint(0,T) | T
	phi = (p-1)*(q-1)
	while XGCD(e,phi)[0] != 1:
		p = randint(0,T) | T
		q = randint(0,T) | T
		phi = (p-1)*(q-1)
	n = p*q
	d = inv_mod(e,phi)
	print("P")
	print(p)
	f = open("rsa_p","w")
	f.write(str(p))
	f.close()
	print("\n")
	print("Q")
	print(q)
	f = open("rsa_q","w")
	f.write(str(q))
	f.close()
	print("\n")
	print("N")
	print(n)
	f = open("rsa_n","w")
	f.write(str(n))
	f.close()
	print("\n")
	print("D")
	print(d)
	f = open("rsa_d","w")
	f.write(str(d))
	f.close()

def decrypt(m):
	f = open("rsa_p","r")
	p = int(f.read())
	f.close()

	f = open("rsa_q","r")
	q = int(f.read())
	f.close()

	f = open("rsa_n","r")
	n = int(f.read())
	f.close()

	f = open("rsa_d","r")
	d = int(f.read())
	f.close()

	return pow_mod(m,d,n)


