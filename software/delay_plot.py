from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

import numpy as np
import time
import matplotlib.pyplot as plt

#data = [0,0,0,0,0,0,0,0,0]
data = np.linspace(0, 1027, 1028).astype(int)
i = 1

def delay_end(fig) :
    window.after(4,lambda:delay_end(fig))
    for i in range(len(data)):
        data[i] = data[i - 1] + 1
    print(data)
    # plotting the graph
    fig.axes[0].set_ylim((min(data),max(data)))
    fig.axes[0].lines[0].set_ydata(data)
    window.update()
    canvas.draw()

def after_function(fig) :
    for i in range(len(data)):
        data[i] = data[i - 1] + 1
    print(data)
    # plotting the graph
    fig.axes[0].set_ylim((min(data),max(data)))
    fig.axes[0].lines[0].set_ydata(data)
    window.update()
    canvas.draw()

def Reset_unreset() :

    print("RESET")
    #des.ResetDES()
    time.sleep(3)
    ################################## UNRESET #############################################
    print("unRESET")
    #des.unResetDES()

def Injection() :
    file_name = open('Signal_ADC_20keV.txt', "r")
    lines = file_name.readlines()
    formated_lines = []
    for elm in lines:
        formated_lines.append(int(elm[:-1]))
    print("############################################")
    print("file name fichier injecté {}".format(file_name))
    #print("print formated lines {}".format(formated_lines)) #### print liste ONE file
    print("min ", min(formated_lines))
    print("max ", max(formated_lines))
    print("max-min", max(formated_lines)-min(formated_lines))

    #################################### write formated_lines to pipe in INJECTION ##########################################

    print("############## INJection #####################")
    list_pipe_in_array = np.array(formated_lines)
    # print("list_pipe_in_array{}".format(list_pipe_in_array))
    adresse = 0x80
    #des.setpipein(list_pipe_in_array, adresse)

def get_entry_TH(event) :
    valeur = v.get()
    print("get_entry_TH:",valeur)
    TH_rise = int(valeur)
    #des.setwire_TH_rise(TH_rise)
    print(TH_rise)

def get_entry_TL(event) :
    valeur = v1.get()
    print("get_entry_TL:",valeur)
    TH_fall = int(valeur)
    #des.setwire_TH_fall(TH_fall)
    print(TH_fall)

# the main Tkinter window
window = Tk()

# the figure that will contain the plot
fig = Figure(figsize=(5, 5),dpi=100)

# adding the subplot
plot1 = fig.add_subplot(111)

# creating the Tkinter canvas
# containing the Matplotlib figure
canvas = FigureCanvasTkAgg(fig,master=window)
canvas.draw()


# placing the canvas on the Tkinter window
canvas.get_tk_widget().pack()

# creating the Matplotlib toolbar
toolbar = NavigationToolbar2Tk(canvas,window)

toolbar.update()

b5 = Button(window, text="RESET", command=Reset_unreset,name="b5") # BOUTON reset
b5.pack()

b6 = Button(window, text="Injection", command=Injection,name="b5") # BOUTON Injection
b6.pack()

label = Label(window, text="get_entry_TH")
v = Entry( window, text="get_entry_TH", bd = 5 )
label.pack()
v.pack()  # pack l'ojb à gui
v.bind('<Return>', get_entry_TH)

label = Label(window, text="get_entry_TL")
v1 = Entry( window, text="get_entry_TL", bd = 5 )
label.pack()
v1.pack()  # pack l'ojb à gui
v1.bind('<Return>', get_entry_TL)

fig.axes[0].plot(data)  #Axes class represents one (sub-)plot in a figure
#canvas.draw()
#window.update()

# draw_idle

delay_end(fig)
#label.after(300, after_function(fig))

# run the gui
window.mainloop()