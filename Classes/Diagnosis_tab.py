from CM4_MBUS_LIB import *
from tkinter import *
import customtkinter as ctk
import serial
import logging
from ChecklistCombobox.checklistcombobox import ChecklistCombobox
from .Device import Device
from tkinter import ttk
from math import floor
from math import log2


class Diagnosis_tab:
    def __init__ (self, root, app):

        self.app = app
        
        RS485_RTU_Master.convigure_overlap_checking(False)

        self.window = Toplevel(root)
        self.window.title('Create Connection')
        self.window.geometry('800x600')
        self.window.grab_set()

        network_identification_frame = LabelFrame(self.window, text='Network Identification', bg='red')
        network_identification_frame.grid(row=0, column=0, sticky='ew')
        self.window.columnconfigure(0, weight = 1)
        self.__fill_network_identification_frame(network_identification_frame)

        fc_identification_frame = LabelFrame(self.window, text='Function Codes Identification', bg='green')
        fc_identification_frame.grid(row=1, column=0, sticky='ew')
        self.__fill_fc_identification_frame(fc_identification_frame)

        address_identification_frame = LabelFrame(self.window, text='Addresses Identification', bg='blue')
        address_identification_frame.grid(row=2, column=0, sticky='ew')
        self.__fill_address_identification_frame(address_identification_frame)

    def __fill_network_identification_frame(self, frame: LabelFrame):
        from .App import App
        network_identification_settings_frame = LabelFrame(frame, text='Network Identification Settings')
        network_identification_settings_frame.grid(column=0,row=0, sticky='w')
        frame.columnconfigure(0, weight= 1)

        network_identification_settings_frame_left = Frame(network_identification_settings_frame)
        network_identification_settings_frame_left.grid(column=0,row=0, sticky='w')
        frame.columnconfigure(0, weight= 1)
        
        self.com_port_combo = self.__create_param('COM Port', App.COMS, network_identification_settings_frame_left)
        self.bool_identify_devices = BooleanVar(value=False)
        devices_checkbox = Checkbutton(network_identification_settings_frame_left,text='identify devices', variable=self.bool_identify_devices, command=self.__update_network_time)
        devices_checkbox.pack()
        di_start_button = Button(network_identification_settings_frame_left, text='start', command= self.__start_network_identification)
        di_start_button.pack()
        self.network_time_label = Label(network_identification_settings_frame_left, text='Expected time:')
        self.network_time_label.pack()
        self.network_progress_var = IntVar()
        self.network_progress_bar = ttk.Progressbar(network_identification_settings_frame_left, variable=self.network_progress_var)
        self.network_progress_bar.pack()

        network_identification_settings_frame_middle = Frame(network_identification_settings_frame)
        network_identification_settings_frame_middle.grid(column=1,row=0, sticky='e')

        from_label = Label(network_identification_settings_frame_middle, text='Minimal Address')
        from_label.pack()
        self.network_from_entry = Entry(network_identification_settings_frame_middle)
        self.network_from_entry.pack()
        self.network_from_entry.insert(0, str(0))
        self.network_from_entry.bind('<FocusOut>', self.__update_network_time)
        self.network_from_entry.bind('<Return>', self.__update_network_time)
        to_label = Label(network_identification_settings_frame_middle, text='Maximal Address')
        to_label.pack()

        self.network_to_entry = Entry(network_identification_settings_frame_middle)
        self.network_to_entry.pack()
        self.network_to_entry.insert(0, str(248))
        self.network_to_entry.bind('<FocusOut>', self.__update_network_time)
        self.network_to_entry.bind('<Return>', self.__update_network_time)

        network_identification_settings_frame_right = Frame(network_identification_settings_frame)
        network_identification_settings_frame_right.grid(column=2,row=0, sticky='e')
        
        self.network_baudrates_combo_checkbox = ChecklistCombobox(network_identification_settings_frame_right, values = App.BAUDRATES)
        self.network_baudrates_combo_checkbox.pack()
        self.network_baudrates_combo_checkbox.bind('<FocusOut>', self.__update_network_time)
        
        self.network_parities_combo_checkbox = ChecklistCombobox(network_identification_settings_frame_right, values = App.PARITIES)
        self.network_parities_combo_checkbox.pack()
        self.network_parities_combo_checkbox.bind('<FocusOut>', self.__update_network_time)
        
        self.network_stopbits_combo_checkbox = ChecklistCombobox(network_identification_settings_frame_right, values = App.STOPBITS)
        self.network_stopbits_combo_checkbox.pack()
        self.network_stopbits_combo_checkbox.bind('<FocusOut>', self.__update_network_time)
        
        self.network_bytesizes_combo_checkbox = ChecklistCombobox(network_identification_settings_frame_right, values = App.BYTESIZES)
        self.network_bytesizes_combo_checkbox.pack()
        self.network_bytesizes_combo_checkbox.bind('<FocusOut>', self.__update_network_time)

        network_identification_results_frame = LabelFrame(frame, text='Network Identification Results')
        network_identification_results_frame.grid(column=2, row=0, sticky='e')
        frame.columnconfigure(1, weight= 1)

        self.params_label = Label(network_identification_results_frame, text='params:')
        self.params_label.pack()
        self.devices_label = Label(network_identification_results_frame, text='devices:')
        self.devices_label.pack()

    def __fill_fc_identification_frame(self, frame: LabelFrame):

        fc_identification_settings_frame = LabelFrame(frame, text='Function Code Identification Settings')
        fc_identification_settings_frame.grid(column=0,row=0, sticky='w')
        frame.columnconfigure(0, weight= 1)

        self.devices_combo = self.__create_param('Device', ['None'], fc_identification_settings_frame)

        self.fc_combo_checkbox = ChecklistCombobox(fc_identification_settings_frame, values = Device.FUNCTION_CODES)
        self.fc_combo_checkbox.pack()

        self.fci_start_button = Button(fc_identification_settings_frame, text='start', command= self.__start_fc_identification, state=DISABLED)
        self.fci_start_button.pack()

        fc_identification_results_frame = LabelFrame(frame, text='Function Code Identification Results')
        fc_identification_results_frame.grid(column=1, row=0, sticky='e')
        frame.columnconfigure(1, weight= 2)

        self.fc_device_id_label = Label(fc_identification_results_frame, text='Device ID:')
        self.fc_device_id_label.pack()
        self.supported_fc_label = Label(fc_identification_results_frame, text='Supported FCs:')
        self.supported_fc_label.pack()

    def __fill_address_identification_frame(self, frame: LabelFrame):
        
        address_identification_settings_frame = LabelFrame(frame, text='address Identification Settings')
        address_identification_settings_frame.grid(column=0,row=0, sticky='w')
        frame.columnconfigure(0, weight= 1)
        
        self.address_combo_checkbox = ChecklistCombobox(address_identification_settings_frame, values = ['DI', 'Coils', 'IR', 'HR'])
        self.address_combo_checkbox.pack()
        self.address_combo_checkbox.bind('<FocusOut>', self.__update_address_time)
        
        self.address_device_combo = self.__create_param('Slave address', [], address_identification_settings_frame)
        
        from_label = Label(address_identification_settings_frame, text='Minimal Address')
        from_label.pack()
        self.address_from_entry = Entry(address_identification_settings_frame)
        self.address_from_entry.pack()
        self.address_from_entry.insert(0, str(0))
        self.address_from_entry.bind('<FocusOut>', self.__update_address_time)
        self.address_from_entry.bind('<Return>', self.__update_address_time)
        to_label = Label(address_identification_settings_frame, text='Maximal Address')
        to_label.pack()
        self.address_to_entry = Entry(address_identification_settings_frame)
        self.address_to_entry.pack()
        self.address_to_entry.insert(0, str(int(0xFFFF)))
        self.address_to_entry.bind('<FocusOut>', self.__update_address_time)
        self.address_to_entry.bind('<Return>', self.__update_address_time)
        
        self.toghether = BooleanVar(value = False)
        toghether_checkbox = Checkbutton(address_identification_settings_frame,text='all addresses are toghether and start from min', variable=self.toghether, command=self.__update_address_time)
        toghether_checkbox.pack()

        self.ai_start_button = Button(address_identification_settings_frame, text='start', command= self.__start_address_identification, state=DISABLED)
        self.ai_start_button.pack()

        self.address_time_label = Label(address_identification_settings_frame, text='Expected time:')
        self.address_time_label.pack()
        
        address_identification_results_frame = LabelFrame(frame, text='address Identification Results')
        address_identification_results_frame.grid(column=1, row=0, sticky='e')
        frame.columnconfigure(1, weight= 2)

        self.address_slave_label = Label(address_identification_results_frame, text='Slave ID:')
        self.address_slave_label.pack()
        self.address_di_label = Label(address_identification_results_frame, text='DI Addresses:')
        self.address_di_label.pack()
        self.address_coils_label = Label(address_identification_results_frame, text='Coils Addresses:')
        self.address_coils_label.pack()
        self.address_ir_label = Label(address_identification_results_frame, text='IR Addresses:')
        self.address_ir_label.pack()
        self.address_hr_label = Label(address_identification_results_frame, text='HR Addresses:')
        self.address_hr_label.pack()

    def __create_param(self, desc, values, master_window) -> ctk.CTkComboBox :
        frame = Frame(master_window)
        frame.pack()
        label = ctk.CTkLabel(frame, text=desc)
        label.pack()
        combo = ctk.CTkComboBox(frame, values=values)
        combo.pack()
        return combo

    def __start_network_identification(self):
        from .App import App
        self.devices_list = []
        com_port = App.COMS_DICT[self.com_port_combo.get()]

        addresses = range(int(self.network_from_entry.get()), int(self.network_to_entry.get()))
        
        baudrates = self.network_baudrates_combo_checkbox.get()
        if type(baudrates) is str:
            baudrates = [App.BAUDRATE_DICT[baudrates]]
        else:
            baudrates = [App.BAUDRATE_DICT[bdr] for bdr in baudrates]
        
        parities = self.network_parities_combo_checkbox.get()
        if type(parities) is str:
            parities = [App.PARITY_DICT[parities]]
        else:
            parities = [App.PARITY_DICT[par] for par in parities]
        
        stopbits = self.network_stopbits_combo_checkbox.get()
        if type(stopbits) is str:
            stopbits = [App.STOPBITS_DICT[stopbits]]
        else:
            stopbits = [App.STOPBITS_DICT[stb] for stb in stopbits]
        
        bytesizes = self.network_bytesizes_combo_checkbox.get()
        if type(bytesizes) is str:
            bytesizes = [App.BYTESIZE_DICT[bytesizes]]
        else:
            bytesizes = [App.BYTESIZE_DICT[bs] for bs in bytesizes]


        self.__update_network_time()
        self.app.root.update_idletasks()
        self.network_progress_bar.start()
        self.params, self.master = Scanner.identify_network_params(com_port, addresses, baudrates, parities, stopbits, bytesizes, self.network_progress_function)
        logging.info(f'network identified with parameters {self.params}')
        first_adress = self.params['first_address']
        if self.bool_identify_devices.get() :
            self.devices_list = Scanner.list_devices_in_network(self.master, range(first_adress, 248))
            logging.info(f'network identified with addresses {self.devices_list}')
            if self.devices_list:
                self.fci_start_button.config(state=NORMAL)
                self.ai_start_button.config(state=NORMAL)
                values=[str(device) for device in self.devices_list]
                self.devices_combo.configure(values= values)
                self.devices_combo.set(values[0])
                self.address_device_combo.configure(values = values)
                self.address_device_combo.set(values[0])
        self.network_progress_bar.stop()

        self.__update_device_identification_results()

    def __update_device_identification_results(self):
        self.params_label.config(text=f'params: {self.params}')
        self.devices_label.config(text=f'devices: {self.devices_list}')

    def __start_fc_identification(self):
        fc_s = [Device.FUNCTION_CODES_DICT[fc] for fc in self.fc_combo_checkbox.get()]
        supported_fcs = Scanner.list_supportable_fc_in_device(self.master, int(self.devices_combo.get()), fc_s)
        self.fc_device_id_label.config(text=f'Device ID: {self.devices_combo.get()}')
        self.supported_fc_label.config(text=f'Supported FCs: {supported_fcs}')

    def __start_address_identification(self):
        data_type_label_dict = {
            'DI': self.address_di_label,
            'Coils': self.address_coils_label,
            'IR': self.address_ir_label,
            'HR': self.address_hr_label
        }

        from_adr = int(self.address_from_entry.get())
        to_adr = int(self.address_to_entry.get())
        
        data_types = self.address_combo_checkbox.get()
        if type(data_types) is str:
            data_types = [data_types]

        
        self.__update_address_time()
        self.app.root.update_idletasks()

        scanning_function = Scanner.list_supportable_addresses_toghether  if self.toghether.get() else Scanner.list_supportable_addresses

        for data_type in data_types:
            addresses = scanning_function(self.master, int(self.address_device_combo.get()), (from_adr, to_adr), data_type)
            data_type_label_dict[data_type].config(text= f'{data_type} addresses: {addresses}')

    def __update_address_time(self, *_event):
        try:
            from_adr = int(self.address_from_entry.get())
            to_adr = int(self.address_to_entry.get())

            data_types = self.address_combo_checkbox.get()
            if type(data_types) is str:
                data_types = [1]
            
            if self.toghether.get():
                expected_time = 1
            else: 
                expected_time = floor((to_adr-from_adr)*0.014)*len(data_types)

            if expected_time < 60:
                self.address_time_label.config(text=f'Expected time: {expected_time} seconds')
            else:
                self.address_time_label.config(text=f'Expected time: {floor(expected_time/60)} minutes, {expected_time%60} seconds')
        except:
            pass

    def __update_network_time(self, *_event):
        from .App import App
        try:
            
            addresses = range(int(self.network_from_entry.get()), int(self.network_to_entry.get())+1)
            
            baudrates = self.network_baudrates_combo_checkbox.get()
            if type(baudrates) is str:
                baudrates = 1
            else:
                baudrates = len(baudrates)
            
            parities = self.network_parities_combo_checkbox.get()
            if type(parities) is str:
                parities = 1
            else:
                parities = len(parities)
            
            stopbits = self.network_stopbits_combo_checkbox.get()
            if type(stopbits) is str:
                stopbits = 1
            else:
                stopbits = len(stopbits)
            
            bytesizes = self.network_bytesizes_combo_checkbox.get()
            if type(bytesizes) is str:
                bytesizes = 1
            else:
                bytesizes = len(bytesizes)

            addresses_time = len(addresses) if self.bool_identify_devices.get() else 0

            time = baudrates*parities*stopbits*bytesizes+addresses_time
            if time < 60:
                self.network_time_label.config(text=f'Expected time: {time} seconds')
            elif time < 3600:
                self.network_time_label.config(text=f'Expected time: {floor(time/60)} minutes, {time%60} seconds')
            else:
                self.network_time_label.config(text=f'Expected time: {floor(time/3600)} hours, {floor(time/60)%60} minutes')
        except:
            return
        
    def network_progress_function(self, progress):
        self.network_progress_bar['value'] = progress
        self.app.root.update_idletasks()
