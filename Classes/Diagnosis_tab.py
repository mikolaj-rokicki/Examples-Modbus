from CM4_MBUS_LIB import *
from tkinter import *
import customtkinter as ctk
import serial
import logging
from ChecklistCombobox.checklistcombobox import ChecklistCombobox
from .Device import Device


class Diagnosis_tab:
    def __init__ (self, root, app):

        self.app = app
        
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
        self.window.columnconfigure(0, weight = 1)
        self.__fill_fc_identification_frame(fc_identification_frame)

        address_identification_frame = LabelFrame(self.window, text='Addresses Identification', bg='blue')
        address_identification_frame.grid(row=2, column=0, sticky='ew')
        self.window.columnconfigure(0, weight = 1)
        self.__fill_address_identification_frame(address_identification_frame)

        
        

    def __fill_network_identification_frame(self, frame: LabelFrame):
        from .App import App
        network_identification_settings_frame = LabelFrame(frame, text='Network Identification Settings')
        network_identification_settings_frame.grid(column=0,row=0, sticky='w')
        frame.columnconfigure(0, weight= 1)
        
        self.com_port_combo = self.__create_param('COM Port', App.COMS, network_identification_settings_frame)
        self.bool_identify_devices = BooleanVar(value=False)
        devices_checkbox = Checkbutton(network_identification_settings_frame,text='identify devices', variable=self.bool_identify_devices)
        devices_checkbox.pack()
        di_start_button = Button(network_identification_settings_frame, text='start', command= self.__start_network_identification)
        di_start_button.pack()
        
        network_identification_results_frame = LabelFrame(frame, text='Network Identification Results')
        network_identification_results_frame.grid(column=1, row=0, sticky='e')
        frame.columnconfigure(1, weight= 2)

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
        
        self.address_device_combo = self.__create_param('Slave address', [], address_identification_settings_frame)
        
        from_label = Label(address_identification_settings_frame, text='Minimal Address')
        from_label.pack()
        self.from_entry = Entry(address_identification_settings_frame)
        self.from_entry.pack()
        self.from_entry.insert(0, str(0))
        to_label = Label(address_identification_settings_frame, text='Maximal Address')
        to_label.pack()
        self.to_entry = Entry(address_identification_settings_frame)
        self.to_entry.pack()
        self.to_entry.insert(0, str(int(0xFFFF)))
        
        self.toghether = BooleanVar(value = False)
        toghether_checkbox = Checkbutton(address_identification_settings_frame,text='all addresses are toghether and start from min', variable=self.toghether)
        toghether_checkbox.pack()

        self.ai_start_button = Button(address_identification_settings_frame, text='start', command= self.__start_address_identification, state=DISABLED)
        self.ai_start_button.pack()
        
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
        addresses = range(1, 248)
        baudrates = [App.BAUDRATE_DICT[bdr] for bdr in App.BAUDRATES]
        parities = [App.PARITY_DICT[par] for par in App.PARITIES]
        stopbits = [App.STOPBITS_DICT[stb] for stb in App.STOPBITS]
        bytesizes = [App.BYTESIZE_DICT[bs] for bs in App.BYTESIZES]
        self.params, self.master = Scanner.identify_network_params(com_port, addresses, baudrates, parities, stopbits, bytesizes)
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

        from_adr = int(self.from_entry.get())
        to_adr = int(self.to_entry.get())

        scanning_function = Scanner.list_supportable_addresses_toghether if self.toghether.get() else Scanner.list_supportable_addresses

        data_types = self.address_combo_checkbox.get()
        if type(data_types) is str:
            data_types = [data_types]

        for data_type in data_types:
            addresses = scanning_function(self.master, int(self.address_device_combo.get()), (from_adr, to_adr), data_type)
            data_type_label_dict[data_type].config(text= f'{data_type} addresses: {addresses}')
