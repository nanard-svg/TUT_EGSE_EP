import ok
import time
import numpy as np
import math

import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

import matplotlib.pyplot as plt

init_spectrum = False

def clr_graph() :
    global init_spectrum
    init_spectrum = True
    # tk.messagebox.showinfo("showinfo", "init_spectrum = {}".format(init_spectrum))


############################### classe OK

array_pipe_out = np.ones(1028).astype(int)
list_array_pipe_out_MSB = []
list_array_pipe_out_LSB = []
list_array_pipe_out1_MSB = []
list_array_pipe_out1_LSB = []
Spectre = [0 for i in range(0, 1023)]
Spectre1 = [0 for i in range(0, 1023)]


#################################### global setting ######################################

mode_adc = 1 # set to one if ADC use
reset_ram = 1 # set to one if clear RAM spectrum
continuous_ready  = 1 # generally set to one set to zero if filter analysis
start_capture  = 0

#################################### CLASS ######################################

class DESTester:
    def __init__(self):
        return

    def InitializeDevice(self):
        # Open the first device we find.
        self.xem = ok.FrontPanelDevices().Open()
        if not self.xem:
            print ("A device could not be opened.  Is one connected?")
        else:
            print ("A device is opened")

        # Get some general information about the device.
        self.devInfo = ok.okTDeviceInfo()
        if (self.xem.NoError != self.xem.GetDeviceInfo(self.devInfo)):
            print ("Unable to retrieve device information.")
            return(False)
        print("         Product: " + self.devInfo.productName)
        print("Firmware version: %d.%d" % (self.devInfo.deviceMajorVersion, self.devInfo.deviceMinorVersion))
        print("   Serial Number: %s" % self.devInfo.serialNumber)
        print("       Device ID: %s" % self.devInfo.deviceID)

        # Download the configuration file.
        #if (self.xem.NoError != self.xem.ConfigureFPGA("C:\XEM7310-A75-bitfile\Counters.bit")):
            #print ("FPGA configuration failed.")
        #else:
            #print("FPGA configuration done.")


        # Check for FrontPanel support in the FPGA configuration.
        if (False == self.xem.IsFrontPanelEnabled()):
            print ("FrontPanel support is not available.")
        else:
            print("FrontPanel support is available.")
            return(False)

        print ("FrontPanel support is available.")
        return(True)


    def Close (self) :
        self.xem = ok.FrontPanel().Close()

    def ResetDES(self,param_vals):
        self.xem.SetWireInValue(0x00, param_vals)# ADC mode disable , clear RAM spectre disable, continuous mode disable, reset enable
        self.xem.UpdateWireIns()

    def unResetDES(self,param_vals):
        self.xem.SetWireInValue(0x00, param_vals)# ADC mode disable , clear RAM spectre disable, continuous mode disable, reset disable
        self.xem.UpdateWireIns()

    def start_capture(self,param_vals):
        self.xem.SetWireInValue(0x00, param_vals)# ADC mode disable , clear RAM spectre disable, continuous mode disable, capture start,  reset enable
        self.xem.UpdateWireIns()

    def setwire(self):

        self.xem.SetWireInValue(0x01, level_trig)
        self.xem.UpdateWireIns()

    def setwire_TH_rise(self,TH_rise):

        self.xem.SetWireInValue(0x02, TH_rise)
        self.xem.UpdateWireIns()

    def setwire_TH_fall(self,TH_fall):

        self.xem.SetWireInValue(0x03, TH_fall)
        self.xem.UpdateWireIns()

    def setwire_gain_filtre0(self,gain_filtre0):

        self.xem.SetWireInValue(0x04, gain_filtre0)
        self.xem.UpdateWireIns()

    def setwire_gain_filtre1(self,gain_filtre1):

        self.xem.SetWireInValue(0x05, gain_filtre1)
        self.xem.UpdateWireIns()

    def getwire(self,adress_wire_out_science):
        global get
        self.xem.UpdateWireOuts();
        get = self.xem.GetWireOutValue(adress_wire_out_science)

    def setpipein(self,list_pipe_in,adresse):
        self.xem.WriteToPipeIn(adresse, list_pipe_in)

    def getpipeout(self,adresse_pipe_out_read):
        self.xem.ReadFromPipeOut(adresse_pipe_out_read,array_pipe_out)
        return(array_pipe_out)

def tohex(val, nbits):
  return hex((val + (1 << nbits)) % (1 << nbits))

def pathname1():
    i = tk.b4.winfo_id()
    print("identité", i)
    u = racine.winfo_pathname(i, False)
    print("pathname", u)

def delay_end(fig):

    global init_spectrum
    global Spectre
    global Spectre1

    racine.after(200, lambda:delay_end(fig))
    #print("delay_end")
    #print("############## read pointer spectrum filter 0 #####################")

    adress_wire_out_science = 0x24  # filter 1
    des.getwire(adress_wire_out_science)

    if get == 1028 :
        print("read pointer spectrum filter 1 : {}".format(get))
        #print("################################ READ FIFO  Pipe spectrum filter 0 #############################################")
        adresse_pipe_out_read = 0xA4         #filter1
        des.getpipeout(adresse_pipe_out_read)
        list_array_pipe_out1 = list(array_pipe_out)

        adress_wire_out_science = 0x21  # filter 0
        des.getwire(adress_wire_out_science)

        if get == 1028:
            print("read pointer spectrum filter 0 : {}".format(get))
            # print("################################ READ FIFO  Pipe spectrum filter 0 #############################################")
            adresse_pipe_out_read = 0xA2  # filter1
            des.getpipeout(adresse_pipe_out_read)
            list_array_pipe_out = list(array_pipe_out)

            adress_wire_out_science = 0x24  # filter 0
            des.getwire(adress_wire_out_science)

            #print("################################ DATA of  spectrum filter 1 #############################################")
            for elm in list_array_pipe_out[4:] :
                #print(type(elm))
                #list_array_pipe_out_MSB.append(int(elm/2**16))
                list_array_pipe_out_MSB.append(np.short((elm & 0xFFFF0000)/2**16))
                #print("address : {}".format(np.short((elm & 0xFFFF0000) / 2 ** 16)))
                list_array_pipe_out_LSB.append(np.short(elm & 0xFFFF))
                #print("energy : {}".format(np.short(elm & 0xFFFF)))

                if (np.short(elm & 0xFFFF)) != 0:
                    print("spectrum", tohex(elm, 32))

                    # Construction du spectre
                    add = int(((elm & 0xFFFF0000) / 2 ** 16))  # Ajout GO
                    data = (elm & 0xFFFF)  # Ajout GO
                    Spectre[add] = Spectre[add] + data  # Ajout GO
                    # Spectre[add] = data


            for elm in list_array_pipe_out1[4:]:
                # print(type(elm))
                # list_array_pipe_out_MSB.append(int(elm/2**16))
                list_array_pipe_out1_MSB.append(np.short((elm & 0xFFFF0000) / 2 ** 16))
                # print("address : {}".format(np.short((elm & 0xFFFF0000) / 2 ** 16)))
                list_array_pipe_out1_LSB.append(np.short(elm & 0xFFFF))
                # print("energy : {}".format(np.short(elm & 0xFFFF)))

                if (np.short(elm & 0xFFFF)) != 0:
                    print("spectrum", tohex(elm, 32))

                    # Construction du spectre
                    add = int(((elm & 0xFFFF0000) / 2 ** 16))  # Ajout GO
                    data = (elm & 0xFFFF)  # Ajout GO
                    Spectre1[add] = Spectre1[add] + data  # Ajout GO
                    # Spectre1[add] = data

        # racine.bind("<BackSpace>",  clear_vect())

        if init_spectrum == True :

            Spectre = [0 for i in range(0, 1023)]
            Spectre1 = [0 for i in range(0, 1023)]
            init_spectrum = False
            # tk.messagebox.showinfo("showinfo", "init_spectrum = {}".format(init_spectrum))

        min_1 = min(Spectre)
        min_2 = min(Spectre1)
        max_1 = max(Spectre)
        max_2 = max(Spectre1)


        fig.axes[0].set_ylim(((min(min_1, min_2), max(max_1, max_2))))
        fig.axes[0].lines[0].set_ydata(Spectre)
        fig.axes[0].lines[1].set_ydata(Spectre1)
        #racine.update()
        canvas.draw_idle()

        adress_wire_out_science = 0x25
        des.getwire(adress_wire_out_science)

        print("############################################")
        print("read counter pulse filter 1 add=0x25 {}".format(get))
        print("############################################")

        adress_wire_out_science = 0x22
        des.getwire(adress_wire_out_science)

        print("############################################")
        print("read counter pulse filter 0 add=0x22 {}".format(get))
        print("############################################")

#################################### param ######################################

def param(mode_adc, reset_ram, continuous_ready, start_capture,reset):
    param_vals = 2**31*mode_adc + 2**30*reset_ram + 2**29*continuous_ready + 2**1*start_capture + 2**0*reset

    return param_vals

def Reset_unreset() :

    mode_adc = 1  # set to one if ADC use
    reset_ram = 1  # set to one if clear RAM spectrum
    continuous_ready = 1  # generally set to one set to zero if filter analysis
    start_capture = 0
    reset = 1
    print("RESET")
    des.ResetDES(param(mode_adc, reset_ram, continuous_ready, start_capture, reset))
    time.sleep(2)
    reset = 0
    print("unRESET")
    des.unResetDES(param(mode_adc, reset_ram, continuous_ready, start_capture, reset))
    start_capture = 1

def InitializeDevice() :
    print("------ DES Encrypt/Decrypt Tester in Python ------")

    if (False == des.InitializeDevice()):
        exit
    print("------------------------------------------------------------")

def close() :
    print("button Close")
    des.Close
    print("exit")

    print("\nNb de coups :\nFir1 = {}\nFir2 = {}\n ".format(sum(Spectre), sum(Spectre1)))

    racine.destroy()
    racine.quit()

# def clear_vect(Spectre):
    # Spectre = [0 for i in range(0, 1023)]
    # print("####################################################################################################")



def Injection() :

    mode_adc = 0  # set to one if ADC use
    #reset_ram = 1  # set to one if clear RAM spectrum
    #continuous_ready = 0  # generally set to zero set to one if filter analysis
    #start_capture = 1

    print("injection")
    des.start_capture(param(mode_adc, reset_ram, continuous_ready, start_capture, reset))

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
    des.setpipein(list_pipe_in_array, adresse)

def ADC() :

    mode_adc = 1  # set to one if ADC use
    #reset_ram = 1  # set to one if clear RAM spectrum
    #continuous_ready = 0  # generally set to zero set to one if filter analysis
    #start_capture = 1

    print("ADC")
    des.start_capture(param(mode_adc, reset_ram, continuous_ready, start_capture, reset))

def get_entry_TH(event) :
    valeur = v.get()
    print("get_entry_TH:",valeur)
    TH_rise = int(valeur)*32
    des.setwire_TH_rise(TH_rise)
    print(TH_rise)

def get_entry_TL(event) :
    valeur = v1.get()
    print("get_entry_TL:",valeur)
    TH_fall = int(valeur)*32
    des.setwire_TH_fall(TH_fall)
    print(TH_fall)

def get_gain_filtre0(event) :
    valeur = v2.get()
    print("get_gain_filtre0:",valeur)
    gain_filtre0 = int(math.log2(int(valeur)))
    des.setwire_gain_filtre0(gain_filtre0)
    print(gain_filtre0)

def get_gain_filtre1(event) :
    valeur = v3.get()
    print("get_gain_filtre1:",valeur)
    gain_filtre1 = int(math.log2(int(valeur)))
    des.setwire_gain_filtre1(gain_filtre1)
    print(gain_filtre1)

racine = tk.Tk() #fait apparaitre fenetre principale

des = DESTester()


# the figure that will contain the plot
fig = Figure(figsize=(5, 5),dpi=100)

# adding the subplot
plot1 = fig.add_subplot(111)

# creating the Tkinter canvas
# containing the Matplotlib figure
canvas = FigureCanvasTkAgg(fig,master=racine)
canvas.draw()

# placing the canvas on the Tkinter window
canvas.get_tk_widget().pack()

# creating the Matplotlib toolbar
toolbar = NavigationToolbar2Tk(canvas,racine)

toolbar.update()

racine.geometry("600x600+500+500")
racine.pack_propagate(0)
racine.title("Main_Win_GSE_3UT")
label = tk.Label(racine, text="GSE GUI 3UT")
label.pack()

#b5 = Button(racine, text="RESET", command=Reset_unreset,name="b5") # BOUTON reset
b6 = tk.Button(racine, text="Injection", command=Injection,name="b6") # BOUTON Injection
b7 = tk.Button(racine, text="ADC", command=ADC,name="b7") # BOUTON Injection
#b8 = Button(racine, text="Close Opal Kelly", command=close,name="b8") # BOUTON Injection
#b5.pack()
b7.pack()
b6.pack()
#b8.pack()

label = tk.Label(racine, text="level pulse rising : 1->1024")
v = tk.Entry( racine, text="get_entry_TH", bd = 5 )
label.pack()
v.pack()  # pack l'ojb à gui
v.bind('<Return>', get_entry_TH)

label = tk.Label(racine, text="level pulse falling < level pulse rising  : 1->1024")
v1 = tk.Entry( racine, text="get_entry_TL", bd = 5 )
label.pack()
v1.pack()  # pack l'ojb à gui
v1.bind('<Return>', get_entry_TL)

label = tk.Label(racine, text="Gain FIR 1 : 1 -> ~32")
v2 = tk.Entry( racine, text="get_gain_filtre0", bd = 5 )
label.pack()
v2.pack()  # pack l'ojb à gui
v2.bind('<Return>', get_gain_filtre0)

label = tk.Label(racine, text="Gain FIR 2 : 1 -> ~32")
v3 = tk.Entry( racine, text="get_gain_filtre1", bd = 5 )
label.pack()
v3.pack()  # pack l'ojb à gui
v3.bind('<Return>', get_gain_filtre1)

############################### Init OK et Reset before GUI
InitializeDevice()
################################## RESET #############################################

reset  = 1

print ("RESET")
des.ResetDES(param(mode_adc, reset_ram, continuous_ready, start_capture, reset))

time.sleep(2)

################################## UNRESET #############################################

reset  = 0

print ("unRESET")
des.unResetDES(param(mode_adc, reset_ram, continuous_ready, start_capture, reset))
########################################################################################################

#################################  LOAD COEF  ###################################################
print ("Coef")
file = open('coef_V2.txt', "r")
lines_coef = file.readlines()
formated_lines_coef = []
for elm in lines_coef :
    formated_lines_coef.append(int(elm[:-1]))##la liste lines a des eleementr ascii dont on supprime\n avec :-1
    #formated_lines.append(elm[:-1])

#print("la liste coef est \n {}".format(formated_lines_coef))
list_pipe_in_array = np.array(formated_lines_coef)
#print("le tableau coef est \n {}".format(list_pipe_in_array))
adresse=0x81  # filter0
des.setpipein(list_pipe_in_array,adresse)

print ("Coef")
file = open('coef_V2_1.txt', "r")
lines_coef_1 = file.readlines()
formated_lines_coef_1 = []
for elm in lines_coef_1 :
    formated_lines_coef_1.append(int(elm[:-1]))##la liste lines a des eleementr ascii dont on supprime\n avec :-1
    #formated_lines.append(elm[:-1])

#print("la liste coef est \n {}".format(formated_lines_coef))
list_pipe_in_array_1 = np.array(formated_lines_coef_1)
#print("le tableau coef est \n {}".format(list_pipe_in_array))
adresse=0x82 # filter1
des.setpipein(list_pipe_in_array_1,adresse)

###################################  SET LEVEL TRIGG  ###############################################
print ("set trigger_level")
#level_trig=0xFFFF8EB8
level_trig=5
level_trig=int(np.uint32(level_trig))
print(level_trig)
des.setwire()

print ("set trigger_TH_rise")
#level_trig=0xFFFF8EB8
TH_rise=62*32
TH_rise=int(np.uint32(TH_rise))
print(TH_rise)
des.setwire_TH_rise(TH_rise)

print ("set trigger_TH_fall")
#level_trig=0xFFFF8EB8
TH_fall=62*32
TH_fall=int(np.uint32(TH_fall))
print(TH_fall)
des.setwire_TH_fall(TH_fall)

valeur = 1
print("get_gain_filtre0:", valeur)
gain_filtre0 = int(math.log2(int(valeur)))
des.setwire_gain_filtre0(gain_filtre0)
print(gain_filtre0)

valeur = 1
print("get_gain_filtre1:", valeur)
gain_filtre1 = int(math.log2(int(valeur)))
des.setwire_gain_filtre0(gain_filtre1)
print(gain_filtre0)

###################################  START CAPTURE  ###############################################

start_capture  = 1
reset_ram = 1 # set to one if clear RAM spectrum

print ("start_capture")
des.start_capture(param(mode_adc, reset_ram, continuous_ready, start_capture, reset))

###################################  IRQ time  ###############################################

fig.axes[0].plot(Spectre, label = "FIR 1")  #Axes class represents one (sub-)plot in a figure
fig.axes[0].plot(Spectre1, label = "FIR 2")  #Axes class represents one (sub-)plot in a figure
fig.legend()
fig.supxlabel("raw")
fig.supylabel("Count number")

delay_end(fig)

##################################
######### Bouton quitter #########
##################################

racine.protocol(name="WM_DELETE_WINDOW", func = lambda : close())
racine.bind("<Escape>", lambda e : close())
racine.bind("<Delete>", lambda cl : clr_graph())
# racine.bind("<BackSpace>", lambda cl : clear_graph())
##################################  MAIN GUI ###################################################
racine.mainloop()
print("Affichage commandé après ARRET de mainloop")