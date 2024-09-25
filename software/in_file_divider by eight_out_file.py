import numpy as np
import math

import matplotlib.pyplot as plt
import numpy as np

print ("divider by 16")
file_name_out = f"in_file.txt"
file = open(file_name_out, "r")
lines = file.readlines()

formated_lines_before = []
formated_lines_hex_before = []

for elm in lines :
    formated_lines_before.append((int(elm[:-1])))##la liste lines a des eleementr ascii dont on supprime\n avec :-1
    #print(formated_lines_before)

for elm in formated_lines_before :
    formated_lines_hex_before.append((round(elm/16)))
    #print(formated_lines_hex_before)

file_name_out = f"out_file.txt"
file = open(file_name_out, "w")
for items in formated_lines_hex_before:
    file.write('%s\n' % items)
file.close()

plt.subplot(211)
plt.plot(formated_lines_before)
plt.title("in filter")
plt.xlabel("temps")
plt.ylabel("amplitude")
plt.subplot(212)
plt.plot(formated_lines_hex_before)
plt.title("out filter")
plt.xlabel("temps")
plt.ylabel("amplitude")
plt.show()