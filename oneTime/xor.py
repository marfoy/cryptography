import base64

fileA = open("exhibitA","r")
fileB = open("exhibitB","r")

xor = []
while 1:
	A = fileA.read(1)
	B = fileB.read(1)
	if A == None or B == None:
		break;
	xor.append(ord(A)^ord(B))

fileA.close()
fileB.close()
fileC = open("xorFile","wb")
fileC.write(xor)
fileC.close()

