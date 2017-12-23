#Get CTF flag from binary file using a shift cipher

text = open('ch7.bin','rb').read()

i = -176
while i < 177:
    tmp = ""
    try:
    	for c in text:
		tmp = tmp + chr(ord(c) + i)
	print tmp
    except:
    	print "Shift is too large : " + str(i)
    i += 1
