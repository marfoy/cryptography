from primal_test import *
import math
import time
from random import randint, seed
from equaLin.inv_mod import *

c_time = time.time()
g=load_int("log_32_g")
p=load_int("log_32_p")
h=load_int("log_32_h")
T = 2**16
h_table = {}
x = 0
temp = 1
while x < T:
	h_table[temp % p] = x
	temp*=g
	x = x + 1
	print(100*float(x)/T)

S = inv_mod(temp,p)
u = h
print("here 1")
i = 0
while 1:
	if u in h_table.keys():
		x = i*T + h_table[u]
		print(x)
		break
	else:
		u = (u *S) % p
		i += 1
print("here 2")
print(time.time()-c_time)
print(pow_mod(g,x,p) == h % p)
