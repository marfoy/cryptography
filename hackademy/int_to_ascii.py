def ascii_to_int(string):
	int_m = ""
	for c in string:
		int_m+=str(ord(c))
	return int(int_m)

def int_to_ascii(n):
	cipher = str(n)
	text = ""
	x = 0
	while x < len(cipher):
		if cipher[0] == 1:
			text += chr(int(cipher[x:x+3]))
			x+=3
		else:
			text += chr(int(cipher[x:x+2]))
			x+=2
	return text

m = "coucou"
print(int_to_ascii(ascii_to_int(m)))

