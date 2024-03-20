import ok
import time
# import keyboard
# import array as arr

#import math
import matplotlib.pyplot as plt
import numpy as np

plt.close('all')

count = 0
count_data = 0
ligne = 0
i = 0
indice=0
lignes = []
list_array_pipe_out_MSB = []
list_array_pipe_out_LSB = []


#list_pipe_in_array = np.ones(2048).astype(int)

#list_pipe_in = np.linspace(0,511,512).astype(int)
#list_pipe_in_array = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13 ,14 ,15 ,16 ,15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,0,-1, -2, -3, -4, -5, -6, -7, -8, -9, -10, -11, -12, -13 ,-14 ,-15 ,-16 ,-15, -14, -13, -12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1,0])


array_pipe_out = np.ones(1028).astype(int)

#################################################
#list_pipe_in = np.array(ma_liste)
#ma_list = list(mon_tab)
###############################################

#################################### global setting ######################################

mode_adc = 1 # set to one if ADC use
reset_ram = 1 # set to one if clear RAM spectrum
continuous_ready  = 0 # generally set to zero set to one if filter analysis
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

    def setwire_TH_rise(self):

        self.xem.SetWireInValue(0x02, TH_rise)
        self.xem.UpdateWireIns()

    def setwire_TH_fall(self):

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

#################################### param ######################################

def param(mode_adc, reset_ram, continuous_ready, start_capture,reset):
    param_vals = 2**31*mode_adc + 2**30*reset_ram + 2**29*continuous_ready + 2**1*start_capture + 2**0*reset

    return param_vals

#################################### Main code ######################################

print ("------ DES Encrypt/Decrypt Tester in Python ------")
des = DESTester()
if (False == des.InitializeDevice()):
    pass
print ("------------------------------------------------------------")
time.sleep(1)
################################## RESET #############################################

reset  = 1

print ("RESET")
des.ResetDES(param(mode_adc, reset_ram, continuous_ready, start_capture, reset))

time.sleep(3)

################################## UNRESET #############################################

reset  = 0

print ("unRESET")
des.unResetDES(param(mode_adc, reset_ram, continuous_ready, start_capture, reset))

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
adresse=0x81
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
level_trig=10
level_trig=int(np.uint32(level_trig))
print(level_trig)
des.setwire()

print ("set trigger_TH_rise")
#level_trig=0xFFFF8EB8
TH_rise=2000
TH_rise=int(np.uint32(TH_rise))
print(TH_rise)
des.setwire_TH_rise()

print ("set trigger_TH_fall")
#level_trig=0xFFFF8EB8
TH_fall=2000
TH_fall=int(np.uint32(TH_fall))
print(TH_fall)
des.setwire_TH_fall()

##############################  Initialisation du graph  ##########################################

Spectre_Add = np.linspace(0, 1027, 1028).astype(int)
Spectre = np.zeros(1028).astype(int)  # Ajout GO

plt.ion() # Ajout GO
fig_spectre = plt.figure("Spectre 3UTransat") # Ajout GO
line, = plt.plot(Spectre_Add, Spectre)
plt.xlabel("Raw data") # Ajout GO
plt.ylabel("Count number") # Ajout GO
plt.title("Spectre 3UTransat") # Ajout GO
plt.show()

###################################  START CAPTURE  ###############################################

start_capture  = 1

print ("start_capture")
des.start_capture(param(mode_adc, reset_ram, continuous_ready, start_capture, reset))

try :
    while (True) :
        
        for c in range(10):

            print("############## read pointer spectrum filter 0 #####################")
            adress_wire_out_science = 0x21  # filter 0
            # adress_wire_out_science = 0x24 #filter1
            des.getwire(adress_wire_out_science)
            while (get != 1028):
                # print("############################################")
                # print("read pointer spectrum  {}".format(get))
                # print("############################################")
                des.getwire(adress_wire_out_science)
            print("read pointer spectrum filter 0 : {}".format(get))

            print("############## read pointer spectrum #####################")
            adress_wire_out_science = 0x24 # 21 for filter 0
            des.getwire(adress_wire_out_science)
            while (get != 1028):
                #print("############################################")
                #print("read pointer spectrum  {}".format(get))
                #print("############################################")
                des.getwire(adress_wire_out_science)
            print("read pointer spectrum : {}".format(get))
    
            # Spectre_Add = np.linspace(0, 1027, 1028).astype(int)
            # Spectre = np.zeros(1028).astype(int)  # Ajout GO

            print("################################ READ FIFO  Pipe spectrum filter 0 #############################################")
            adresse_pipe_out_read = 0xA2  # filter0
            # adresse_pipe_out_read = 0xA4        #filter1
            des.getpipeout(adresse_pipe_out_read)
            # print(array_pipe_out.itemsize)
            # print("print array_pipe_out  {}".format(array_pipe_out))
            list_array_pipe_out = list(array_pipe_out)

            #print("################################ READ FIFO  Pipe spectrum #############################################")
            adresse_pipe_out_read=0xA4 # A2 for filter 0
            des.getpipeout(adresse_pipe_out_read)
            #print(array_pipe_out.itemsize)
            #print("print array_pipe_out  {}".format(array_pipe_out))
            list_array_pipe_out = list(array_pipe_out)
    
            # print("################################ READ header spectrum #############################################")
            print("index ram spectrum : {}".format(tohex(list_array_pipe_out[0],32)))
            print("TIME MSB : {}".format(tohex(list_array_pipe_out[1],32)))
            print("TIME  : {}".format(tohex(list_array_pipe_out[2],32)))
            print("TIME LSB  : {}".format(tohex(list_array_pipe_out[3],32)))
    
            ################### SPLITE 32 bit Science from Pipe out spectrum #######################################
    
            for elm in list_array_pipe_out[4:] :
                #list_array_pipe_out_MSB.append(int(elm/2**16))
                list_array_pipe_out_MSB.append(((elm & 0xFFFF0000)/2**16))
                #print("address : {}".format(np.short((elm & 0xFFFF0000) / 2 ** 16)))
                list_array_pipe_out_LSB.append((elm & 0xFFFF))
                #print("energy : {}".format(np.short(elm & 0xFFFF)))
                if (np.short(elm & 0xFFFF)) != 0 :
                    print("spectrum",hex(elm))
    
                    # Construction du spectre
                    add = int(((elm & 0xFFFF0000)/2**16))  # Ajout GO
                    data = (elm & 0xFFFF)  # Ajout GO
                    Spectre[add] = Spectre[add] + data  # Ajout GO
    
            #################################### write formated_lines to pipe in INJECTION ##########################################
    
            # Plot du spectre
            plt.clf()
            plt.plot(Spectre_Add, Spectre)
            plt.pause(0.001)
            plt.show()

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

except KeyboardInterrupt:
    des.Close()
    #  breakpoint()
    print("\n#######################################################\nscript done\n#######################################################")
