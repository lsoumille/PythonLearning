#Shitty code used to retrieve CTF flag from stack content
#reorder bytes because there are in little indian
#then decode hex

s = "000000200804b008b7e552f30000000008049ff400000002bffffc24bffffd4a0000002f0804b00839617044282936646d61704500000a64b7e554adb7fcf3c4b7fff00008048579b656cf0008048570"
cpt2 = 0
res_temp = ""
res = ""
while (cpt2 < len(s) - 7):
    res_temp = ""
    i = 0
    while (i < 8):
        print i
        hexchar = s[cpt2 + i] + s[cpt2 + i + 1]
        res_temp = hexchar + res_temp
        if i == 6:
            res = res + res_temp
        i = i + 2
    cpt2 = cpt2 + 8

print res.decode("hex")
