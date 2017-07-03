concat = open("exhibitConcat","r").read()
for x in range(0,len(concat)):
	print(concat[:len(concat)-1-x])
	print("\n\n\n")
