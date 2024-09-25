import ok
import time
import array as arr

import math
import matplotlib.pyplot as plt
import numpy as np

count = 0
count_data = 0
ligne = 0
i = 0
indice=1
lignes = []
list_array_pipe_out_MSB = []
list_array_pipe_out_LSB = []
param_vals=0


file_names = ['1.txt','2.txt','3.txt','4.txt','5.txt','6.txt']

for file_name in file_names:
#################################### read file from list name ##########################################
    file_name = open(file_name, "r")
    lines = file_name.readlines()
    formated_lines = []
    for elm in lines:
        formated_lines.append(int(elm[:-1]))
    print("############################################")
    print("file name fichier lue {}".format(file_name))
    #print("print formated lines {}".format(formated_lines)) #### print liste ONE file
    #print("min ", min(formated_lines))
    print("max ", max(formated_lines))
    #print("max-min", max(formated_lines)-min(formated_lines))
    formated_lines.remove(max(formated_lines))
    print("second largest",max(formated_lines))
    formated_lines.remove(max(formated_lines))
    print("third largest",max(formated_lines))

    plt.subplot(221)
    plt.plot(formated_lines)
    plt.title("Filter")
    plt.xlabel("temps")
    plt.ylabel("amplitude")

    plt.show()