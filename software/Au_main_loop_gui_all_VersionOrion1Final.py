import ok
import time
import math
# import json
import os
import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt

from tkinter import filedialog, simpledialog, messagebox, ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import datetime as dt

#COnstante égale à 1024 pour bit file utilisé par Aurian, et 256 pour le bit file réellement utilisé
cte_raw_data_size = 256

#################################### gestion en temporelles ####################################


#################################### Bibliothèque OpalKelly ####################################

# Classe pour controler le périphérique Opal Kelly
class DeviceController:
    def __init__(self):
        self.xem = None
        self.devInfo = None
        
    # Méthode pour initialiser le périphérique
    def initialize_device(self):
        self.xem = ok.FrontPanelDevices().Open()
        if not self.xem:
            print("A device could not be opened. Is one connected?")
            return False
        print("A device is opened")
        
        self.devInfo = ok.okTDeviceInfo()
        if self.xem.NoError != self.xem.GetDeviceInfo(self.devInfo):
            print("Unable to retrieve device information.")
            return False

        print(f"Product: {self.devInfo.productName}")
        print(f"Firmware version: {self.devInfo.deviceMajorVersion}.{self.devInfo.deviceMinorVersion}")
        print(f"Serial Number: {self.devInfo.serialNumber}")
        print(f"Device ID: {self.devInfo.deviceID}")

        if not self.xem.IsFrontPanelEnabled():
            print("FrontPanel support is not available.")
            return False

        print("FrontPanel support is available.")
        return True
        

    # Méthode pour fermer le périphérique
    def close_device(self):
        self.xem = ok.FrontPanel().Close()
    
    # Méthode pour réinitialiser le DES
    def reset_des(self, param_vals):
        #print("paramettre dans reset = {}".format(param_vals))
        self.xem.SetWireInValue(0x00, param_vals)  
        self.xem.UpdateWireIns()
        
    # Méthode pour sortir de l'état de réinitialisation du DES
    def unreset_des(self, param_vals):
        print("paramettre dans unreset = {}".format(param_vals))
        self.xem.SetWireInValue(0x00, param_vals)  
        self.xem.UpdateWireIns()

    # Méthode renommée pour démarrer la capture du périphérique
    def start_capture_device(self, param_vals):
        self.xem.SetWireInValue(0x00, param_vals)  
        self.xem.UpdateWireIns()

    def enable_high_filter(self, param_vals):
        print("paramettre dans enable_high_filter = {}".format(param_vals))
        self.xem.SetWireInValue(0x00, param_vals)
        self.xem.UpdateWireIns()

    # Méthode pour définir un niveau de fil
    def set_wire(self, level_trig):
        self.xem.SetWireInValue(0x01, level_trig)
        self.xem.UpdateWireIns()

    # Méthode pour définir le seuil de montée
    def set_wire_th_rise(self, th_rise):
        self.xem.SetWireInValue(0x02, th_rise)
        self.xem.UpdateWireIns()
        self.xem.SetWireInValue(0x08, th_rise)
        self.xem.UpdateWireIns()
        TH_ADC=1023*32
        self.xem.SetWireInValue(0x07, TH_ADC)
        self.xem.UpdateWireIns()

    # Méthode pour définir le seuil de descente
    def set_wire_th_fall(self, th_fall):
        self.xem.SetWireInValue(0x03, th_fall)
        self.xem.UpdateWireIns()
        self.xem.SetWireInValue(0x09, th_fall)
        self.xem.UpdateWireIns()

    # Méthode pour définir le gain du Filtre0
    def setwire_gain_filtre0(self,gain_filtre0):
        self.xem.SetWireInValue(0x04, gain_filtre0)
        self.xem.UpdateWireIns()
        self.xem.SetWireInValue(0x0A, gain_filtre0)
        self.xem.UpdateWireIns()
        
    # Méthode pour définir le gain du Filtre1
    def setwire_gain_filtre1(self,gain_filtre1):
        self.xem.SetWireInValue(0x05, gain_filtre1)
        self.xem.UpdateWireIns()
        self.xem.SetWireInValue(0x0B, gain_filtre1)
        self.xem.UpdateWireIns()

    # Méthode pour définir le DAC et le ON OFF
    def setwire_DAC(self,DAC_VAL_conv):
        self.xem.SetWireInValue(0x06, DAC_VAL_conv)
        self.xem.UpdateWireIns()

    # Méthode pour obtenir la valeur d'un fil
    def get_wire(self, address_wire_out):
        self.xem.UpdateWireOuts()
        get = self.xem.GetWireOutValue(address_wire_out)
        #print("\nget = {}".format(get))
        return get

    # Méthode pour écrire dans un tube d'entrée
    def set_pipe_in(self, data, address):
        self.xem.WriteToPipeIn(address, data)

    # Méthode pour lire depuis un tube de sortie
    def get_pipe_out(self, address):
        data = np.ones(1028).astype(int)
        self.xem.ReadFromPipeOut(address, data)
        return data

    # Méthode pour lire depuis un tube de sortie
    def get_pipe_out_sd(self, address):
        data = np.ones(12).astype(int)
        self.xem.ReadFromPipeOut(address, data)
        return data

#################################### Classes pour la gestion des données et de l'interface ####################################

# Classe pour traiter les données
class DataProcessor:
    def __init__(self):
        self.array_pipe_out = np.ones(1028).astype(int)
        self.list_array_pipe_out_MSB = []
        self.list_array_pipe_out_LSB = []
        self.list_array_pipe_out1_MSB = []
        self.list_array_pipe_out1_LSB = []
        self.spectre = [0 for _ in range(1024)]
        self.spectre1 = [0 for _ in range(1024)]
            
        self.init_spectrum = False

    # Méthode pour traiter les données
    def process_data(self, data):
        list_array_pipe_out = list(data)
        for elm in list_array_pipe_out[4:]:
            self.list_array_pipe_out_MSB.append(np.short((elm & 0xFFFF0000) / 2**16))
            self.list_array_pipe_out_LSB.append(np.short(elm & 0xFFFF))
            if np.short(elm & 0xFFFF) != 0:
                print("spectrum = {}".format(self.tohex(elm, 32)))
                add = int(((elm & 0xFFFF0000) / 2**16))
                data = (elm & 0xFFFF)
                self.spectre[add] = self.spectre[add] + data
        
        return self.spectre
    
    def process_data1(self, data):
        list_array_pipe_out1 = list(data)
        
        for elm in list_array_pipe_out1[4:]:
            self.list_array_pipe_out1_MSB.append(np.short((elm & 0xFFFF0000) / 2**16))
            self.list_array_pipe_out1_LSB.append(np.short(elm & 0xFFFF))
            
            if np.short(elm & 0xFFFF) != 0:
                print("spectrum = {}".format(self.tohex(elm, 32)))
                add = int(((elm & 0xFFFF0000) / 2**16))
                data = (elm & 0xFFFF)
                self.spectre1[add] = self.spectre1[add] + data
                
        return self.spectre1
    
    # Méthode pour convertir une valeur en hexadécimal
    def tohex(self, val, nbits):
        return hex((val + (1 << nbits)) % (1 << nbits))
    


class GUIManager:
    def __init__(self, root, device_controller, data_processor, data_processor1, application):
        self.root = root
        self.device_controller = device_controller
        self.data_processor = data_processor
        self.application = application
        
        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.plot1 = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.root)



        # self.v = tk.StringVar()
        # self.v1 = tk.StringVar()
        # self.Entry_Gain_FIR0 = 0
        # self.Entry_Gain_FIR1 = 0
        # self.rising_pulseTH_tk = 0
        # self.rising_pulseTL_tk = 0
        
        self.threshold1 = 62
        self.threshold2 = 62
        self.gain1 = 1
        self.gain2 = 1
        self.valeur = 0
        self.integration_time = 4294967295
        self.current_time = 0
        
        self.coef_1 = {}
        self.coef_2 = {}

        self.DAC_VAL = 0
        self.DET_VAL = 0

        self.selected_file = 'Signal_ADC_100keV.txt' 

        self.initialize_gui()
        self.creat_menu()
        
#        self.control_panel()
        self.setting_table()
        
        


    # Méthode pour initialiser l'interface utilisateur
    def initialize_gui(self):
        # titre 1
        self.root.title("Data Acquisition of EGSE System ")

        # barre d'outils
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.root.bind('<Escape>', self.close_opal_kelly)
        self.root.bind('<Delete>', self.clear_graph)
        self.root.protocol(name="WM_DELETE_WINDOW", func=lambda: self.close_opal_kelly)

        # titre 2
        title_label = tk.Label(self.root, text="GSE GUI 3UT")
        title_label.pack()
     
    # def control_panel(self):
    #     control_panel = tk.Frame(self.root)
    #     control_panel.pack(side=tk.BOTTOM, fill=tk.X)
        
    #     # Ajouter le bouton pour afficher les données temporelles
    #     btn_show_temporal = tk.Button(control_panel, text="Show Temporal Data", command=self.open_temporal_window)
    #     btn_show_temporal.pack(side=tk.LEFT)
    
    def setting_table(self):
        self.tree = ttk.Treeview(self.root, columns=("Parameter(s)", "Value(s)"), show="headings")
        self.tree.heading("Parameter(s)", text="Parameter(s)")
        self.tree.heading("Value(s)", text="Value(s)")
        self.tree.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.real_time_update_table()
    
    def real_time_update_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        self.tree.insert("", "end", values=("High threshold |FIR1|", self.threshold1))
        self.tree.insert("", "end", values=("Low threshold |FIR2|", self.threshold2))
        self.tree.insert("", "end", values=("Gain |FIR1|", self.gain1))
        self.tree.insert("", "end", values=("Gain |FIR2|", self.gain2))
        self.tree.insert("", "end", values=("DAC", self.DAC_VAL))
        self.tree.insert("", "end", values=("Detector status", self.DET_VAL))
        self.tree.insert("", "end", values=("Integration Time", self.integration_time))
        self.tree.insert("", "end", values=("Current Time", self.current_time))
        self.root.after(200, self.real_time_update_table)
  
#################################################################################################    
    def open_temporal_window(self):
        temporal_window = tk.Toplevel(self.root)
        temporal_window.title("Temporal Data")
        temporal_window.geometry("800x600")
        
        self.temporal_window = Figure(figsize=(5, 5), dpi=100)
        self.plot1 = self.temporal_window.add_subplot(211)
        self.canvas = FigureCanvasTkAgg(self.temporal_window, master=self.root)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        
        
        plt.plot(self.application.list_array_pipe_out_LSB_0)
        plt.plot(self.application.list_array_pipe_out_MSB_0)
        plt.title("Filter 0")
        plt.xlabel("temps")
        plt.ylabel("amplitude")
        plt.subplot(212)
        plt.plot(self.applicationlist_array_pipe_out_LSB)
        plt.plot(self.applicationlist_array_pipe_out_MSB)
        plt.title("Filter 1")
        plt.xlabel("temps")
        plt.ylabel("amplitude")
        plt.show()
        self.canvas.draw_idle()

        self.application.show_temporal_data()
####################################################################################################      
    
    def creat_menu(self):
        # generating a menu bar
        menubar = tk.Menu(self.root)
        
        # Adding setting data in the toolbar menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        
        # settings_menu.add_command(label="Set Threshold", underline=4, accelerator= "CTRL+T", command= lambda: self.set_threshold(self.valeur))
        settings_menu.add_command(label="Set Integration Time", underline=4, accelerator= "CTRL+I", command= lambda: self.set_integration_time(self.valeur))
        settings_menu.add_command(label="Set Rising Pulse (0 to 1024)", underline=4, accelerator= "CTRL+R", command= lambda: self.rising_pulse_TH_tk(self.valeur))
        settings_menu.add_command(label="Set Falling Pulse (0 to 1024)", underline=4, accelerator= "CTRL+L", command= lambda: self.rising_pulse_TL_tk(self.valeur))     
        settings_menu.add_command(label="Set Gain Filter0 (0 to 32)", underline=4, accelerator= "CTRL+G", command= lambda: self.gain_of_filter0(self.valeur))
        settings_menu.add_command(label="Set Gain Filter1 (0 to 32)", underline=5, accelerator= "CTRL+A", command= lambda: self.gain_of_filter1(self.valeur))
        settings_menu.add_command(label="Set DAC Value (0 to 4095)", underline=5, accelerator= "CTRL+P", command= lambda: self.get_DAC(self.valeur))
        settings_menu.add_command(label="Set DETECTOR ON (1) OFF (0)", underline=5, accelerator= "CTRL+O", command= lambda: self.get_DET_ON_OFF(self.valeur))
        settings_menu.add_separator()
        #settings_menu.add_command(label="Exit", underline=1, accelerator= "CTRL+X", command=self.quit)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        # self.root.bind_all("<Control-t>", lambda x: self.set_threshold(self.valeur))
        self.root.bind_all("<Control-i>", lambda x: self.set_integration_time(self.valeur))
        self.root.bind_all("<Control-R>", lambda x: self.rising_pulse_TH_tk(self.valeur))
        self.root.bind_all("<Control-l>", lambda x: self.rising_pulse_TL_tk(self.valeur))
        self.root.bind_all("<Control-g>", lambda x: self.gain_of_filter0(self.valeur))
        self.root.bind_all("<Control-a>", lambda x: self.gain_of_filter1(self.valeur))
        #self.root.bind_all("<Control-x>", lambda x: self.quit())
        self.root.bind_all("<Control-p>", lambda x: self.get_DAC(self.valeur))
        self.root.bind_all("<Control-o>", lambda x: self.get_DET_ON_OFF(self.valeur))

        # Adding push and save file in the toolbar menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save Spectrum", underline=0, accelerator= "CTRL+S", command=self.save_spectrum)
        file_menu.add_command(label="Select Injection File", underline=0, accelerator= "CTRL+J", command=self.set_injection_file)
        file_menu.add_command(label="Set Filter Config (coef) ", underline=10, accelerator= "CTRL+C", command= self.set_filter_config)
        file_menu.add_command(label="Set Filter Config 1 (coef) ", underline=10, accelerator= "CTRL+M", command= self.set_filter_config1)
        #file_menu.add_command(label="Load Filter Config", underline=0, accelerator= "CTRL+L", command=self.load_filter_config)
        file_menu.add_separator()
        menubar.add_cascade(label="File", menu=file_menu)
        
        self.root.bind_all("<Control-s>", lambda x: self.save_spectrum())
        self.root.bind_all("<Control-c>", lambda x: self.set_filter_config())
        self.root.bind_all("<Control-m>", lambda x: self.set_filter_config1())
        self.root.bind_all("<Control-j>", lambda x: self.set_injection_file())
        
        
        
        # Adding launch data in the toolbar menu
        DataConfiguration_menu = tk.Menu(menubar, tearoff=0)
        DataConfiguration_menu.add_command(label="Data from ADC", underline=0, command=self.adc)
        DataConfiguration_menu.add_command(label="Data from Injection", underline=0, command=self.injection)
        DataConfiguration_menu.add_separator()
        menubar.add_cascade(label="Configurations", menu=DataConfiguration_menu)
        
        # Adding close and reset in the toolbar menu
        systemConfiguration_menu = tk.Menu(menubar, tearoff=0)
        #systemConfiguration_menu.add_command(label="Reset of OpalKelly", underline=0, command=self.Reset_unreset)
        systemConfiguration_menu.add_command(label="Enable_high_frequency_filter", underline=0,command=self.Enable_high_frequency_filter)
        systemConfiguration_menu.add_command(label="Close system", underline=0, command=self.close_opal_kelly)
        systemConfiguration_menu.add_separator()
        menubar.add_cascade(label="Gestion", menu=systemConfiguration_menu)
        
        self.root.config(menu=menubar)

        
#               #               #              Menu fonctions configuration               #               #               #       

    def set_filter_config(self):
        # permet de choisir un fichier de configuration avce la fonction askopenfilename qui retourne le chemin du fichier selectionnée
        self.application.selected_filter_config = filedialog.askopenfilename(title="Select Filter Config File", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        
        if self.application.selected_filter_config:
            
            print("_")
            
            self.coef_1 = {}
            
            print(f"Coef Filter 0: {self.application.selected_filter_config}")
            with open(self.application.selected_filter_config, "r") as file:
                lines_coef = file.readlines()
            formated_lines_coef = [int(elm.strip()) for elm in lines_coef]
            list_pipe_in_array = np.array(formated_lines_coef)
            #print(f"list_pipe_in_array: {list_pipe_in_array}")
            self.application.device_controller.set_pipe_in(list_pipe_in_array, 0x81)
            
            self.coef_1 = formated_lines_coef.tolist()
            
            print("_")
           
            messagebox.showinfo("Fichier sélectionné", f"Fichier d'injection: {self.application.selected_filter_config}")
        else:
            print("Aucun fichier sélectionné.")
            messagebox.showwarning("Aucun fichier", "Aucun fichier n'a été sélectionné pour l'injection.")

            # permet d'assigner le fichier (objet) a la variable file
            # with open(self.application.selected_filter_config, 'r') as file:
            #     # lit le contenu du fichier, normalement en format json dan snotre cas. ce fichier est placer dans une variable config. 
            #     config = json.load(file)
            #     # appel comme argument de la fonction set_filter_config. ps: "self.root est un aurte objet qui possede une methode."
            #     self.get_selected_filter_config(config)
            #     messagebox.showinfo("Info", "Filter configuration set successfully.")
                
    def set_filter_config1(self):
        
        # permet de choisir un fichier de configuration avce la fonction askopenfilename qui retourne le chemin du fichier selectionnée
        self.application.selected_filter_config1 = filedialog.askopenfilename(title="Select Filter Config File", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        
        if self.application.selected_filter_config1:
            
            print("_")
            
            self.coef_2 = {}
            
            print(f"Coef Filter 1: {self.application.selected_filter_config1}")
            with open(self.application.selected_filter_config1, "r") as file:
                lines_coef_1 = file.readlines()
            formated_lines_coef_1 = [int(elm.strip()) for elm in lines_coef_1]
            list_pipe_in_array_1 = np.array(formated_lines_coef_1)
            #print(f"list_pipe_in_array_1: {list_pipe_in_array_1}")
            self.application.device_controller.set_pipe_in(list_pipe_in_array_1, 0x82)
            
            self.coef_2 = formated_lines_coef_1.tolist()
            
            print("_")
            
            messagebox.showinfo("Fichier sélectionné", f"Fichier d'injection: {self.application.selected_filter_config1}")
        else:
            print("Aucun fichier sélectionné.")
            messagebox.showwarning("Aucun fichier", "Aucun fichier n'a été sélectionné pour l'injection.")
        
            # # permet d'assigner le fichier (objet) a la variable file
            # with open(self.application.selected_filter_config1, 'r') as file:
            #     # lit le contenu du fichier, normalement en format json dan notre cas. ce fichier est placer dans une variable config. 
            #     config1 = json.load(file)
            #     # appel comme argument de la fonction set_filter_config. ps: "self.root est un aurte objet qui possede une methode."
            #     self.get_selected_filter_config(config1)
            #     messagebox.showinfo("Info", "Filter configuration set successfully.")
    
    
    
    ###############################################################################################################################          
    def  save_spectrum(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        
        if file_path:    
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            fichier = open(file_path, "w")
            
            # np.savetxt(file_path, self.application.data_processor.spectre,self.application.data_processor1.spectre1)
            print(f"Spectrum saved to {file_path}")
            
            fichier.write("{};\n".format(file_path))
            today = dt.date.today()
            fichier.write ("Date : {}\n" .format (today).replace("-","/"))


            fichier.write("Version FirmWare ; {}.{}\n".format(0,0))
            fichier.write("Version Software ; {}.{}\n".format(0,0))
            
            fichier.write("High threshold ; {}\n".format(self.threshold1))
            fichier.write("Low threshold ; {}\n".format(self.threshold2))
            fichier.write("Saturation level ; {}\n".format(1023))
            fichier.write("Gain 1 ; {}\n".format(self.gain1))
            fichier.write("Gain 2 ; {}\n".format(self.gain1))
            fichier.write("Acquisition duration ; {}\n".format(self.current_time))
            
            fichier.write("FIR coeficients;\n")
            
            for i in range (len(self.coef_1)):
                
                fichier.write("{};{}\n".format(int(self.coef_1[i]),int(self.coef_2[i])))
               
        
            fichier.write("Spectra;\n")
            
            for i in range(len(self.application.data_processor.spectre)):
                
                fichier.write("{};{}\n".format(int(self.application.data_processor.spectre[i]),int(self.application.data_processor1.spectre1[i])))
        
            fichier.close()
        


    ###################################################################################################   
    
    
    
    
    def set_threshold(self, valeur):
        # demander a l'utilisateur de rentrer une varable flottante
        threshold = simpledialog.askinteger("Input", "Enter threshold value:", initialvalue = valeur)
        # recupere la flottante si l'itilisateur a valider son saisie ou pas et s'assure que la valeur s'execute
        if threshold is not None:
            # appel de la fonction associer a l'argument "threshold"
            self.get_threshold(threshold)

              
    def set_integration_time(self, valeur):
        integration_time_tk = simpledialog.askinteger("Input", "Enter integration time(s) value:", initialvalue = valeur)
        
        if integration_time_tk is not None:
            self.integration_time = integration_time_tk
            self.get_integration_time(integration_time_tk)


    def rising_pulse_TH_tk(self, valeur):
        rising_pulseTH_tk = simpledialog.askinteger("Input", "Enter pulse(s) rising for TH value:", initialvalue = valeur)
        
        if rising_pulseTH_tk is not None:
            self.threshold1 = rising_pulseTH_tk
            self.get_entry_th(rising_pulseTH_tk)


    def rising_pulse_TL_tk(self, valeur):
        rising_pulseTL_tk = simpledialog.askinteger("Input", "Enter pulse(s) rising for TL value:", initialvalue = valeur)
        
        if rising_pulseTL_tk is not None:
            self.threshold2 = rising_pulseTL_tk
            self.get_entry_tl(rising_pulseTL_tk)


    def gain_of_filter0(self, valeur):
        filter0 = simpledialog.askinteger("Input", "Enter gain value:", initialvalue = valeur)
        
        if filter0 is not None:
            self.gain1 = filter0
            self.get_gain_filtre0(filter0)
        
        
    def gain_of_filter1(self, valeur):
        filter1 = simpledialog.askinteger("Input", "Enter gain value:", initialvalue = valeur)
        
        if filter1 is not None:
            self.gain2 = filter1
            self.get_gain_filtre1(filter1)

    def get_DAC(self, valeur):
        DAC_VAL_ask = simpledialog.askinteger("Input", "Enter DAC value:", initialvalue=valeur)

        if DAC_VAL_ask is not None:
            self.DAC_VAL = DAC_VAL_ask
            self.get_DAC_VAL(self.DAC_VAL, self.DET_VAL)

    def get_DET_ON_OFF(self, valeur):
        DET_VAL_ask = simpledialog.askinteger("Input", "Enter Detector ON (1) OFF (0) :", initialvalue=valeur)

        if DET_VAL_ask is not None:
            self.DET_VAL = DET_VAL_ask
            self.get_DAC_VAL(self.DAC_VAL, self.DET_VAL)
        
#               #               #               fonction permettant la mise a jours des graphiques              #               #     

    # Méthode pour mettre a jour le graphique
    def update_plot(self, spectre,spectre1):
        
        xlim = self.plot1.get_xlim()
        ylim = self.plot1.get_ylim()
        
        # print("--------------------------------- xlim = {}".format(xlim))   
        
        x_range_min = int(max(0, xlim[0]))
        x_range_max =int(min(1023, xlim[1]))
        
        self.plot1.clear()
        self.plot1.plot(spectre, 'r-', marker = '')
        self.plot1.plot(spectre1, 'orange', marker = '')
        
        self.plot1.set_xlim(xlim)
        self.plot1.set_ylim(ylim)
        
        self.plot1.set_ylim((min(spectre[int(x_range_min):int(x_range_max)]), max(spectre[int(x_range_min):int(x_range_max)])))
        self.plot1.set_ylim((min(spectre1[int(x_range_min):int(x_range_max)]), max(spectre1[int(x_range_min):int(x_range_max)])))
        
        # self.canvas.draw()
        self.canvas.draw_idle()
        
    def clear_graph(self, init_spectrum):
        
        self.application.init_spectrum = True
        
        print("refresh of the plot")


#               #               #               fonctions permettant la mise a jours des parametres               #               #               #

    # Méthode pour récupérer la valeur du seuil de montée
    def get_entry_th(self, rising_pulseTH_tk):
        valeur = rising_pulseTH_tk
        print(f"get_entry_TH: {valeur}")
        th_rise = int(valeur)*32
        self.device_controller.set_wire_th_rise(th_rise)
        print(th_rise)

    # Méthode pour récupérer la valeur du seuil de descente
    def get_entry_tl(self, rising_pulseTL_tk):
        valeur = rising_pulseTL_tk
        print(f"get_entry_TL: {valeur}")
        th_fall = int(valeur)*32
        self.device_controller.set_wire_th_fall(th_fall)
        print(th_fall)

    # Méthode pour récupérer la valeur du gain du filtre0
    def get_gain_filtre0(self, filter0) :
        #print(f"test filter0 {filter0}")
        valeur = filter0
        print("get_gain_filtre0:",valeur)
        gain_filtre0 = int(math.log2(int(valeur)))
        self.device_controller.setwire_gain_filtre0(gain_filtre0)
        print(gain_filtre0)
    
    # Méthode pour récupérer la valeur du gain du filtre1
    def get_gain_filtre1(self, filter1) :
        valeur = filter1
        print("get_gain_filtre1:",valeur)
        gain_filtre1 = int(math.log2(int(valeur)))
        self.device_controller.setwire_gain_filtre1(gain_filtre1)
        print(gain_filtre1)

    def get_DAC_VAL(self, DAC_VAL, DET_VAL) :
        valeur = DAC_VAL
        status = DET_VAL
        print("get_DAC_VAL: {}\nget_DET_status: {}".format(valeur, status))
        DAC_VAL_conv = valeur + 2**31*status
        self.device_controller.setwire_DAC(DAC_VAL_conv)
        print(DAC_VAL_conv)


    def get_integration_time(self, integration_time_tk):

        pass

    def get_filter_config(self):
        if not self.selected_filter_config:
            self.application.selected_filter_config = 'coef_V2.txt'  # Utilisation du fichier par défaut
            messagebox.showwarning("Aucun fichier", "Aucun fichier n'a été sélectionné pour le filtre 0.")
            print(f"Fichier sélectionné: {self.selected_filter_config}")
        pass
    
    def get_filter_config1(self, config):
        if not self.selected_filter_config1:
            self.application.selected_filter_config = 'coef_V2.txt'  # Utilisation du fichier par défaut
            messagebox.showwarning("Aucun fichier", "Aucun fichier n'a été sélectionné pour le filtre 1.")
            print(f"Fichier sélectionné: {self.selected_filter_config}")
        pass
    
    def get_threshold(self, threshold):

        pass  
    
    # Fonction pour choisir le fichier d'injection
    def set_injection_file(self):
        self.selected_file = filedialog.askopenfilename( title="Choose the injection file", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        
        if self.selected_file:
            print(f"Fichier sélectionné: {self.selected_file}")
            messagebox.showinfo("Fichier sélectionné", f"Fichier d'injection: {self.selected_file}")
        else:
            print("Aucun fichier sélectionné.")
            messagebox.showwarning("Aucun fichier", "Aucun fichier n'a été sélectionné pour l'injection.")

    # Méthode pour gérer l'injection
    def injection(self):
        
        if not self.selected_file:
            self.selected_file = 'Signal_ADC_100keV.txt'  # Utilisation du fichier par défaut
            messagebox.showwarning("Aucun fichier", "Aucun fichier n'a été sélectionné pour l'injection.")
            print(f"Fichier sélectionné: {self.selected_file}")
                        
        # Utiliser le fichier sélectionné ou par défaut
        self.application.mode_adc = 0
        self.application.capture_start = 1
        self.application.reset = 0
        param = self.application.param_values(self.application.enable_high_filter, self.application.continuous_ready, self.application.mode_adc, self.application.capture_start, self.application.reset)
        self.device_controller.start_capture_device(param)

        with open(self.selected_file, "r") as file:
            lines = file.readlines()
        formated_lines = [int(elm.strip()) for elm in lines]
        
        print(f"valeur de la variable mode_adc {self.application.mode_adc}")
        
        print("############################################")
        print(f"file name fichier injection {file.name}")
        print(f"min {min(formated_lines)}")
        print(f"max {max(formated_lines)}")
        print(f"max-min {max(formated_lines) - min(formated_lines)}")

        print("############## INJection #####################")
        list_pipe_in_array = np.array(formated_lines)
        self.device_controller.set_pipe_in(list_pipe_in_array, 0x80)
        messagebox.showinfo("Info", "the launsh of the Numerical Injection set successfully.")
    #########################################################
    # Méthode pour démarrer la capture ADC
    def adc(self):
        self.application.mode_adc = 1
        self.application.capture_start = 1
        self.application.reset = 0
        param = self.application.param_values(self.application.enable_high_filter, self.application.continuous_ready, self.application.mode_adc,  self.application.capture_start, self.application.reset)
        self.device_controller.start_capture_device(param)

        messagebox.showinfo("Info", "the launsh of the ADC set successfully.")

    def Enable_high_frequency_filter(self):
        print("Enable_high_frequency_filter")
        print("Enable_high_frequency_filter")
        print("Enable_high_frequency_filter")
        print("Enable_high_frequency_filter")
        self.application.mode_adc = 1
        self.application.capture_start = 1
        self.application.reset = 0
        self.application.enable_high_filter = 1
        param = self.application.param_values(self.application.enable_high_filter, self.application.continuous_ready, self.application.mode_adc, self.application.capture_start,self.application.reset)
        self.device_controller.enable_high_filter(param)


    # Méthode pour fermer la connexion Opal Kelly
    def close_opal_kelly(self, event=None):
        print("Close Opal Kelly")
        self.device_controller.close_device()
        self.root.quit()
        self.root.destroy()


class Application:
    def __init__(self):
        self.device_controller = DeviceController()
        self.root = tk.Tk()
        self.data_processor = DataProcessor()
        self.data_processor1 = DataProcessor()
        self.gui_manager = GUIManager(self.root, self.device_controller, self.data_processor, self.data_processor1, self)
        
        self.mode_adc = 1
        self.enable_high_filter = 0
        self.continuous_ready = 1
        self.capture_start = 0
        self.reset = 0
        
        self.level_trig = 5
        self.TH_rise = 62*32
        self.TH_fall = 62*32
        
        self.init_spectrum = False
        
        self.selected_filter_config = 'coef_V2.txt'
        self.selected_filter_config1 = 'coef_V2_1.txt'
        
        self.start_time = dt.datetime.now()
        
    # Méthode pour exécuter l'application
    def run(self):
        self.initialize_device()
        self.Reset_unreset()
        self.load_coefficients()
        self.set_trigger_levels()
        self.set_rising_pulse()
        self.set_gain_filtre()
        self.start_capture()
        self.root.mainloop()


    # Méthode pour initialiser le périphérique
    def initialize_device(self):
        print("------ DES Encrypt/Decrypt Tester in Python ------")
        if not self.device_controller.initialize_device():
            pass
        print("------------------------------------------------------------")

    def Reset_unreset(self):
        print("RESET")
        self.capture_start = 0
        self.mode_adc = 1
        self.reset = 1
        self.enable_high_filter = 0
        param = self.param_values(self.enable_high_filter, self.continuous_ready, self.mode_adc, self.capture_start,self.reset)
        print("Param = {}".format(param))
        self.device_controller.reset_des(param)
        print(f"valeur capturestart pour RESET: {self.capture_start}")
        print(f"valeur reset pour RESET: {self.reset}")

        time.sleep(2)

        print("UNRESET")
        self.capture_start = 1
        self.mode_adc = 1
        self.reset = 0

        param = self.param_values(self.enable_high_filter, self.continuous_ready, self.mode_adc, self.capture_start,self.reset)
        # print("Param = {}".format(param))
        self.device_controller.unreset_des(param)
        print(f"valeur capturestart pour RESET: {self.capture_start}")
        print(f"valeur reset pour RESET: {self.reset}")


    # Méthode pour charger les coefficients
    def load_coefficients(self):
        if not self.selected_filter_config:
            self.selected_filter_config = 'coef_V2.txt' # coef par defaut
            # messagebox.showinfo("fichier par defaut","le fichier selectioner par defaut est:",self.selected_filter_config)
        
        self.gui_manager.coef_1 = {}    
        
        print(f"Coef Filter 0: {self.selected_filter_config}")
        with open(self.selected_filter_config, "r") as file:
            lines_coef = file.readlines()
        formated_lines_coef = [int(elm.strip()) for elm in lines_coef]
        list_pipe_in_array = np.array(formated_lines_coef)
        #print(f"list_pipe_in_array: {list_pipe_in_array}")
        self.device_controller.set_pipe_in(list_pipe_in_array, 0x81)
        
        self.gui_manager.coef_1 = formated_lines_coef
        
        if not self.selected_filter_config:
            self.selected_filter_config = 'coef_V2_1.txt' # coef par defaut
            # messagebox.showinfo("fichier par defaut","le fichier selectioner par defaut est:",self.selected_filter_config)
        
        self.gui_manager.coef_2 = {}      
        
        print(f"Coef Filter 1: {self.selected_filter_config1}")
        with open(self.selected_filter_config1, "r") as file:
            lines_coef_1 = file.readlines()
        formated_lines_coef_1 = [int(elm.strip()) for elm in lines_coef_1]
        list_pipe_in_array_1 = np.array(formated_lines_coef_1)
        #print(f"list_pipe_in_array_1: {list_pipe_in_array_1}")
        self.device_controller.set_pipe_in(list_pipe_in_array_1, 0x82)
        
        self.gui_manager.coef_2 = formated_lines_coef_1

    # Méthode pour définir les niveaux de déclenchement
    def set_trigger_levels(self):
        print("set trigger_level")
        self.level_trig = 5
        self.level_trig = int(np.uint32(self.level_trig))
        print(self.level_trig)
        self.device_controller.set_wire(self.level_trig)

    def set_rising_pulse(self):
        print("set trigger_TH_rise")
        self.TH_rise = 62*32
        self.TH_rise = int(np.uint32(self.TH_rise))
        print(self.TH_rise)
        self.device_controller.set_wire_th_rise(self.TH_rise)
        
        print("set trigger_TH_fall")
        self.TH_fall = 62*32
        self.TH_fall = int(np.uint32(self.TH_fall))
        print(self.TH_fall)
        self.device_controller.set_wire_th_fall(self.TH_fall)

    def set_gain_filtre(self):
        print("set_gain_filtre ")
        print("= = = = = = = = = = =")
        valeur = 1
        print("get_gain_filtre0:", valeur)
        gain_filtre0 = int(math.log2(int( valeur)))
        self.device_controller.setwire_gain_filtre0(gain_filtre0)
        print(gain_filtre0)
        print("get_gain_filtre1:", valeur)
        gain_filtre1 = int(math.log2(int( valeur)))
        self.device_controller.setwire_gain_filtre0(gain_filtre1)
        print(gain_filtre1)
    
    # Méthode pour démarrer la capture
    def start_capture(self):
        print("start_capture")
        param = self.param_values(self.enable_high_filter, self.continuous_ready, self.mode_adc, capture_start = 1, reset = 0)
        self.device_controller.start_capture_device(param)
        self.gui_manager.fig.axes[0].plot(self.data_processor.spectre, label = "FIR0" ,color = 'tab:red')
        self.gui_manager.fig.axes[0].plot(self.data_processor1.spectre1, label = "FIR1", color = 'tab:orange')
        self.gui_manager.fig.legend()
        self.delay_end(self.gui_manager.fig)

    # Méthode pour obtenir les valeurs des paramètres
    def param_values(self, mode_adc, enable_high_filter, continuous_ready, capture_start, reset): 
        param_vals = 2**31 * self.mode_adc + 2**30 * self.enable_high_filter + 2**29 * self.continuous_ready + 2**1 * capture_start + 2**0 * reset 
        return (param_vals)

    def show_temporal_data(self):
        
        list_array_pipe_out_MSB = []
        list_array_pipe_out_LSB = []
        list_array_pipe_out_MSB_0 = []
        list_array_pipe_out_LSB_0 = []
        self.param = 0
    
        print(" +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("RESET")
        self.capture_start = 0
        self.reset = 1
        self.param = self.param_values(self.enable_high_filter, self.continuous_ready, self.mode_adc, self.capture_start, self.reset)
        #print("Param = {}".format(param))
        self.device_controller.reset_des(self.param)
        print(f"valeur capturestart pour RESET: {self.capture_start}")
        print(f"valeur reset pour RESET: {self.reset}")
        
        time.sleep(2)

        print("UNRESET")
        self.capture_start = 1
        self.reset = 0
        self.param = self.param_values(self.enable_high_filter, self.continuous_ready, self.mode_adc, self.capture_start, self.reset)
        #print("Param = {}".format(param))
        self.device_controller.unreset_des(self.param)
        print(f"valeur capturestart pour RESET: {self.capture_start}")
        print(f"valeur reset pour RESET: {self.reset}")
        print(" +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        # self.Reset_unreset()
        
        
        print(f"Coef Filter 0: {self.selected_filter_config}")
        with open(self.selected_filter_config, "r") as file:
            lines_coef = file.readlines()
        formated_lines_coef = [int(elm.strip()) for elm in lines_coef]
        list_pipe_in_array = np.array(formated_lines_coef, dtype = np.int32)
        #print(f"list_pipe_in_array: {list_pipe_in_array}")
        self.device_controller.set_pipe_in(list_pipe_in_array, 0x81)
        
        print(f"Coef Filter 1: {self.selected_filter_config1}")
        with open(self.selected_filter_config1, "r") as file:
            lines_coef_1 = file.readlines()
        formated_lines_coef_1 = [int(elm.strip()) for elm in lines_coef_1]
        list_pipe_in_array_1 = np.array(formated_lines_coef_1, dtype = np.int32)
        #print(f"list_pipe_in_array_1: {list_pipe_in_array_1}")
        self.device_controller.set_pipe_in(list_pipe_in_array_1, 0x82)        
        
        # print("set trigger_level")
        # self.level_trig = -15000
        
        # self.level_trig = int(np.int32(self.level_trig))
        # self.level_trig = int(np.uint32(self.level_trig))
        # print(self.level_trig)
        # self.device_controller.set_wire(self.level_trig)
        
        self.level_trig = np.int32(-15000)
        print(self.level_trig)
        self.device_controller.set_wire(self.level_trig)
    
        # print("set trigger_TH_rise")
        # self.TH_rise = -11000
        
        # self.TH_rise = int(np.int32(self.TH_rise))
        # self.TH_rise = int(np.uint32(self.TH_rise))
        # print(self.TH_rise)
        # self.device_controller.set_wire_th_rise(self.TH_rise)  
        
        self.TH_rise = np.int32(-11000)
        print(self.TH_rise)
        self.device_controller.set_wire(self.TH_rise)
    
        # print("set trigger_TH_fall")
        # self.TH_fall = 62*32
        # self.TH_fall = int(np.uint32(self.TH_fall))
        # print(self.TH_fall)
        # self.device_controller.set_wire_th_fall(self.TH_fall)
        
        self.TH_fall = np.int32(62*32)
        print(self.TH_fall)
        self.device_controller.set_wire(self.TH_fall)
        
    
        self.start_capture  = 1
        self.reset  = 0
        self.param = self.param_values(self.enable_high_filter, self.continuous_ready, self.mode_adc, self.capture_start, self.reset)
    
        for c in range(100):
        
            address_wire_out = 0x20
            get = self.device_controller.get_wire(address_wire_out)
            self.device_controller.get_wire(address_wire_out)
            while (get != cte_raw_data_size):
                self.device_controller.get_wire(address_wire_out)
    
            address_wire_out = 0x23
            get = self.device_controller.get_wire(address_wire_out)
            self.device_controller.get_wire(address_wire_out)
            while (get != cte_raw_data_size):
                self.device_controller.get_wire(address_wire_out)
    
            array_pipe_out = np.ones(get).astype(int)
            address_pipe_out_read=0xA3
            self.device_controller.get_pipe_out(address_pipe_out_read)
            list_array_pipe_out = list(array_pipe_out)
    
            array_pipe_out = np.ones(get).astype(int)
            address_pipe_out_read=0xA1
            self.device_controller.get_pipe_out(address_pipe_out_read)
            list_array_pipe_out_0 = list(array_pipe_out)
            
            for elm in list_array_pipe_out:
                list_array_pipe_out_MSB.append(np.short((elm & 0xFFFF0000) >> 16))
                list_array_pipe_out_LSB.append(np.short(elm & 0xFFFF))
             
            # for elm in list_array_pipe_out:
            #     list_array_pipe_out_MSB.append(np.short((elm & 0xFFFF0000) / 2 ** 16))
            #     list_array_pipe_out_LSB.append(np.short(elm & 0xFFFF))
            
            for elm in list_array_pipe_out_0:
                list_array_pipe_out_MSB_0.append(np.short((elm & 0xFFFF0000) >> 16))
                list_array_pipe_out_LSB_0.append(np.short(elm & 0xFFFF))
    
            # for elm in list_array_pipe_out_0:
            #     list_array_pipe_out_MSB_0.append(np.short((elm & 0xFFFF0000)/2**16))
            #     list_array_pipe_out_LSB_0.append(np.short(elm & 0xFFFF))
    
    
    def delay_end(self, fig):    
       self.root.after(200, lambda: self.delay_end(fig))
       
       #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   
       address_wire_out = 0x21    # fliter0
       get = self.device_controller.get_wire(address_wire_out)
       
       current_time = dt.datetime.now()
       
       diff_time = current_time - self.start_time
           
       if  get == 1028:
           #print("get == 1028")
           #print(f"read pointer spectrum filter 0: {get}")
           address_pipe_out_read = 0xA2
           data = self.device_controller.get_pipe_out(address_pipe_out_read)
           
           ####################################################
           if diff_time.total_seconds() < self.gui_manager.integration_time :
               self.gui_manager.current_time = diff_time.total_seconds()
               spectre = self.data_processor.process_data(data)
           ####################################################
           
           # print("\ndata = {}".format(data))
           # print("\nspectre = {}".format(spectre))
           
           #self.gui_manager.update_plot(spectre)
           
       #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
           address_wire_out = 0x24    # fliter1
           get = self.device_controller.get_wire(address_wire_out)
          
           if  get == 1028:
               #print("get == 1028")
               #print(f"read pointer spectrum filter 1: {get}")
               address_pipe_out_read = 0xA4
               data1 = self.device_controller.get_pipe_out(address_pipe_out_read)
               ####################################################
               if diff_time.total_seconds() < self.gui_manager.integration_time :
                   spectre1 = self.data_processor1.process_data1(data1)
               ####################################################
               # print("\nspectre1 = {}".format(spectre1))
               # print("\ndata = {}".format(data1))
       
               self.gui_manager.update_plot(spectre, spectre1)

               address_wire_out = 0x26  # filter 0 SD
               get = self.device_controller.get_wire(address_wire_out)

               if get == 12:
                   print("############# Spectrum filter 0 standard definition #########################################################")
                   print("read pointer spectrum filter 0 standard definition : {}".format(get))
                   adresse_pipe_out_read = 0xA5  # filter0
                   data1 = self.device_controller.get_pipe_out_sd(adresse_pipe_out_read)
                   list_array_pipe_out_standard_definition = list(data1)

                   for element in list_array_pipe_out_standard_definition:
                       print("spectrum SD filter 0", self.data_processor1.tohex(element, 32))

                   address_wire_out = 0x28
                   get = self.device_controller.get_wire(address_wire_out)

                   print("############################################")
                   print("read counter pulse filter Standard definition 0 add=0x28 {}".format(get))
                   print("############################################")

                   address_wire_out = 0x27  # filter 1 SD
                   get = self.device_controller.get_wire(address_wire_out)
                   print("###############################################################################################################")

                   if get == 12:
                       print("############# Spectrum filter 1 standard definition #########################################################")
                       print("read pointer spectrum filter 1 standard definition : {}".format(get))
                       adresse_pipe_out_read = 0xA6  # filter1
                       data1 = self.device_controller.get_pipe_out_sd(adresse_pipe_out_read)
                       list_array_pipe_out_standard_definition = list(data1)

                       for element in list_array_pipe_out_standard_definition:
                           print("spectrum SD filter 1", self.data_processor1.tohex(element, 32))

                       address_wire_out = 0x29
                       get = self.device_controller.get_wire(address_wire_out)

                       print("############################################")
                       print("read counter pulse filter Standard definition 1 add=0x29 {}".format(get))
                       print("############################################")

                       # print("################################ DATA of  spectrum filter 1 #############################################")
                       print("###############################################################################################################")

                       address_wire_out = 0x25
                       self.device_controller.get_wire(address_wire_out)

                       print("############################################")
                       print(f"read counter pulse filter 1 add=0x25 {self.device_controller.get_wire(address_wire_out)}")
                       print("############################################")

                       address_wire_out = 0x22
                       self.device_controller.get_wire(address_wire_out)
                       print("############################################")
                       print(f"read counter pulse filter 0 add=0x22 {self.device_controller.get_wire(address_wire_out)}")
                       print("############################################")

                       print(f"valeur de la variable mode_adc {self.mode_adc}")

       if self.init_spectrum == True :

           self.data_processor.spectre = [0 for _ in range(1024)]
           self.data_processor1.spectre1 = [0 for _ in range(1024)]
           self.init_spectrum = False
           self.start_time = dt.datetime.now()
           # self.gui_manager.update_plot.plot1.clear()
               #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #
               

       

if __name__ == "__main__":

    app = Application()
    app.run()

