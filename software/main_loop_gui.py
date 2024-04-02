import ok
import time
import numpy as np

from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

import matplotlib.pyplot as plt

from tkinter import *
from tkinter import ttk
############################### classe OK

array_pipe_out = np.ones(1028).astype(int)
list_array_pipe_out_MSB = []
list_array_pipe_out_LSB = []
Spectre = [0 for i in range(0, 1023)]


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
    i = b4.winfo_id()
    print("identité", i)
    u = racine.winfo_pathname(i, False)
    print("pathname", u)

def delay_end(fig):
    racine.after(200, lambda:delay_end(fig))
    #print("delay_end")
    #print("############## read pointer spectrum filter 0 #####################")
    adress_wire_out_science = 0x21  # filter 0
    des.getwire(adress_wire_out_science)

    if get == 1028 :
        print("read pointer spectrum filter 0 : {}".format(get))
        #print("################################ READ FIFO  Pipe spectrum filter 0 #############################################")
        adresse_pipe_out_read=0xA2         #filter0
        #adresse_pipe_out_read = 0xA4        #filter1
        des.getpipeout(adresse_pipe_out_read)
        list_array_pipe_out = list(array_pipe_out)

        #print("################################ HEADER spectrum filter 0 #############################################")
        #print("Number Filter and Index Ram Spectrum : {}".format(tohex(list_array_pipe_out[0],32)))
        #print(type(list_array_pipe_out[0]))
        #print("TIME MSB : {}".format(tohex(list_array_pipe_out[1],32)))
        #print("TIME  : {}".format(tohex(list_array_pipe_out[2],32)))
        #print("TIME LSB  : {}".format(tohex(list_array_pipe_out[3],32)))

        #print("################################ DATA of  spectrum filter 0 #############################################")
        for elm in list_array_pipe_out[4:] :
            #print(type(elm))
            #list_array_pipe_out_MSB.append(int(elm/2**16))
            list_array_pipe_out_MSB.append(np.short((elm & 0xFFFF0000)/2**16))
            #print("address : {}".format(np.short((elm & 0xFFFF0000) / 2 ** 16)))
            list_array_pipe_out_LSB.append(np.short(elm & 0xFFFF))
                #print("energy : {}".format(np.short(elm & 0xFFFF)))
            if (np.short(elm & 0xFFFF)) != 0 :
                print("spectrum",tohex(elm,32))

                # Construction du spectre
                add = int(((elm & 0xFFFF0000) / 2 ** 16))  # Ajout GO
                data = (elm & 0xFFFF)  # Ajout GO
                Spectre[add] = Spectre[add] + data  # Ajout GO

                fig.axes[0].set_ylim((min(Spectre), max(Spectre)))
                fig.axes[0].lines[0].set_ydata(Spectre)
                #racine.update()
                canvas.draw_idle()

                list_array_pipe_out = np.linspace(0, 1027, 1028).astype(int)

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
    racine.destroy()


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
    TH_rise = int(valeur)
    des.setwire_TH_rise(TH_rise)
    print(TH_rise)

def get_entry_TL(event) :
    valeur = v1.get()
    print("get_entry_TL:",valeur)
    TH_fall = int(valeur)
    des.setwire_TH_fall(TH_fall)
    print(TH_fall)


racine = Tk() #fait apparaitre fenetre principale

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
label = Label(racine, text="GSE GUI 3UT")
label.pack()

#b5 = Button(racine, text="RESET", command=Reset_unreset,name="b5") # BOUTON reset
b6 = Button(racine, text="Injection", command=Injection,name="b6") # BOUTON Injection
b7 = Button(racine, text="ADC", command=ADC,name="b7") # BOUTON Injection
b8 = Button(racine, text="Close Opal Kelly", command=close,name="b8") # BOUTON Injection
#b5.pack()
b7.pack()
b6.pack()
b8.pack()

label = Label(racine, text="get_entry_TH")
v = Entry( racine, text="get_entry_TH", bd = 5 )
label.pack()
v.pack()  # pack l'ojb à gui
v.bind('<Return>', get_entry_TH)

label = Label(racine, text="get_entry_TL")
v1 = Entry( racine, text="get_entry_TL", bd = 5 )
label.pack()
v1.pack()  # pack l'ojb à gui
v1.bind('<Return>', get_entry_TL)

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
TH_rise=2000
TH_rise=int(np.uint32(TH_rise))
print(TH_rise)
des.setwire_TH_rise(TH_rise)

print ("set trigger_TH_fall")
#level_trig=0xFFFF8EB8
TH_fall=2000
TH_fall=int(np.uint32(TH_fall))
print(TH_fall)
des.setwire_TH_fall(TH_fall)


###################################  START CAPTURE  ###############################################

start_capture  = 1
reset_ram = 1 # set to one if clear RAM spectrum

print ("start_capture")
des.start_capture(param(mode_adc, reset_ram, continuous_ready, start_capture, reset))

###################################  IRQ time  ###############################################

fig.axes[0].plot(Spectre)  #Axes class represents one (sub-)plot in a figure

delay_end(fig)

##################################  MAIN GUI ###################################################
racine.mainloop()
print("Affichage commandé après ARRET de mainloop")