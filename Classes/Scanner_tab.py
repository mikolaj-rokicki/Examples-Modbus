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


class Scanner_tab:
    def __init__ (self, root, app):

        self.app = app
        
        RS485_RTU_Master.convigure_overlap_checking(False)

        self.window = Toplevel(root)
        self.window.title('Create Connection')
        self.window.geometry('1000x900')
        self.window.grab_set()
        main_frame = Frame(self.window)
        main_frame.pack(expand=1, fill='both')
        info_frame = Frame(self.window)
        info_frame.pack(expand=1, fill=X)

        network_identification_frame = LabelFrame(main_frame, text='Network Identification')
        network_identification_frame.grid(row=0, column=0, sticky='ew')
        main_frame.columnconfigure(0, weight = 1)
        self.__fill_network_identification_frame(network_identification_frame)

        fc_identification_frame = LabelFrame(main_frame, text='Function Codes Identification')
        fc_identification_frame.grid(row=1, column=0, sticky='ew')
        self.__fill_fc_identification_frame(fc_identification_frame)

        address_identification_frame = LabelFrame(main_frame, text='Addresses Identification')
        address_identification_frame.grid(row=2, column=0, sticky='ew')
        self.__fill_address_identification_frame(address_identification_frame)

        self.info_label = Label(info_frame, text='ready')
        self.info_label.pack(anchor='e', padx=5)

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
 

        network_identification_settings_frame_middle = Frame(network_identification_settings_frame)
        network_identification_settings_frame_middle.grid(column=1,row=0, sticky='e')

        from_label = Label(network_identification_settings_frame_middle, text='Minimal Address')
        from_label.pack()
        self.network_from_entry = Entry(network_identification_settings_frame_middle)
        self.network_from_entry.pack()
        self.network_from_entry.insert(0, str(1))
        self.network_from_entry.bind('<FocusOut>', self.__update_network_time)
        self.network_from_entry.bind('<Return>', self.__update_network_time)
        to_label = Label(network_identification_settings_frame_middle, text='Maximal Address')
        to_label.pack()

        self.network_to_entry = Entry(network_identification_settings_frame_middle)
        self.network_to_entry.pack()
        self.network_to_entry.insert(0, str(247))
        self.network_to_entry.bind('<FocusOut>', self.__update_network_time)
        self.network_to_entry.bind('<Return>', self.__update_network_time)

        network_identification_settings_frame_right = Frame(network_identification_settings_frame)
        network_identification_settings_frame_right.grid(column=2,row=0, sticky='e')
        
        self.baudradrates_touples = self.__create_checkboxes(network_identification_settings_frame_right, 'Baudrates:', App.BAUDRATES, self.__update_network_time)
        self.parities_touples = self.__create_checkboxes(network_identification_settings_frame_right, 'Parities:', App.PARITIES, self.__update_network_time)
        self.stopbits_touples = self.__create_checkboxes(network_identification_settings_frame_right, 'Stopbits:', App.STOPBITS, self.__update_network_time)


        network_identification_results_frame = LabelFrame(frame, text='Network Identification Results')
        network_identification_results_frame.grid(column=2, row=0, sticky='e')
        frame.columnconfigure(1, weight= 1)

        self.params_label = Label(network_identification_results_frame, text='params:')
        self.params_label.pack()
        self.devices_label = Label(network_identification_results_frame, text='devices:')
        self.devices_label.pack()

    def __create_checkboxes(self, master_frame, label_text, values, command = None):
        checkboxes_frame = Frame(master_frame)
        checkboxes_frame.pack(side=LEFT)
        text = Label(checkboxes_frame, text=label_text)
        text.pack()

        touples = [(BooleanVar(value=True), val) for val in values]
        baudradrates_checkbuttons = [Checkbutton(checkboxes_frame, variable=var, text=txt, command=command if command else None) for var, txt in touples]
        for checkbutton in baudradrates_checkbuttons:
            checkbutton.pack(anchor='w')
        return touples

    def __fill_fc_identification_frame(self, frame: LabelFrame):

        fc_identification_settings_frame = LabelFrame(frame, text='Function Code Identification Settings')
        fc_identification_settings_frame.grid(column=0,row=0, sticky='w')
        frame.columnconfigure(0, weight= 1)

        fc_other_frame = Frame(fc_identification_settings_frame)
        fc_other_frame.pack(side=LEFT, padx=(5, 10))

        self.devices_combo = self.__create_param('Slave address', ['None'], fc_other_frame)

        self.fci_start_button = Button(fc_other_frame, text='start', command= self.__start_fc_identification, state=DISABLED)
        self.fci_start_button.pack()

        fc_checkbox_frame = Frame(fc_identification_settings_frame)
        fc_checkbox_frame.pack(side=RIGHT, padx=(10, 5))        
        self.fc_touples = self.__create_checkboxes(fc_checkbox_frame, 'Checked FC\'s', Device.FUNCTION_CODES)

        fc_identification_results_frame = LabelFrame(frame, text='Function Code Identification Results')
        fc_identification_results_frame.grid(column=2, row=0, sticky='e')
        frame.columnconfigure(1, weight= 2)

        self.fc_device_id_label = Label(fc_identification_results_frame, text='Device ID:')
        self.fc_device_id_label.pack()
        self.supported_fc_label = Label(fc_identification_results_frame, text='Supported FCs:')
        self.supported_fc_label.pack()

    def __fill_address_identification_frame(self, frame: LabelFrame):
        
        address_identification_settings_frame = LabelFrame(frame, text='address Identification Settings')
        address_identification_settings_frame.grid(column=0,row=0, sticky='w')
        frame.columnconfigure(0, weight= 1)
        address_identification_settings_frame_left = LabelFrame(address_identification_settings_frame)
        address_identification_settings_frame_left.pack(side=LEFT)
        address_identification_settings_frame_right = LabelFrame(address_identification_settings_frame)
        address_identification_settings_frame_right.pack(side=LEFT)
        
        
        
        self.address_device_combo = self.__create_param('Slave address', [], address_identification_settings_frame_left)
        
        from_label = Label(address_identification_settings_frame_left, text='Minimal Address')
        from_label.pack()
        self.address_from_entry = Entry(address_identification_settings_frame_left)
        self.address_from_entry.pack()
        self.address_from_entry.insert(0, str(0))
        self.address_from_entry.bind('<FocusOut>', self.__update_address_time)
        self.address_from_entry.bind('<Return>', self.__update_address_time)
        to_label = Label(address_identification_settings_frame_left, text='Maximal Address')
        to_label.pack()
        self.address_to_entry = Entry(address_identification_settings_frame_left)
        self.address_to_entry.pack()
        self.address_to_entry.insert(0, str(int(0xFFFF)))
        self.address_to_entry.bind('<FocusOut>', self.__update_address_time)
        self.address_to_entry.bind('<Return>', self.__update_address_time)
        
        self.toghether = BooleanVar(value = False)
        toghether_checkbox = Checkbutton(address_identification_settings_frame_left,text='all addresses are toghether and start from min', variable=self.toghether, command=self.__update_address_time)
        toghether_checkbox.pack()

        self.ai_start_button = Button(address_identification_settings_frame_left, text='start', command= self.__start_address_identification, state=DISABLED)
        self.ai_start_button.pack()

        self.address_time_label = Label(address_identification_settings_frame_left, text='Expected time:')
        self.address_time_label.pack()

        self.data_types_touples = self.__create_checkboxes(address_identification_settings_frame_right, 'Data Types:', ['DI', 'Coils', 'IR', 'HR'], self.__update_address_time)
        
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
        try:
            from .App import App
            self.devices_list = []
            com_port = App.COMS_DICT[self.com_port_combo.get()]

            from_address = int(self.network_from_entry.get())
            to_address = int(self.network_to_entry.get())
            if from_address > to_address:
                raise ValueError('"from" address bigger than "to" address')
            if from_address < 1:
                raise ValueError('"from" address smaller than 1')
            if to_address > 247:
                raise ValueError('"to" address bigger than 247')
            addresses = range(from_address, to_address)
            
            baudrates = [App.BAUDRATE_DICT[bdr] for checked, bdr in self.baudradrates_touples if checked.get() is True]
            if not baudrates:
                raise Exception('baudrates cannot be empty')
            parities = [App.PARITY_DICT[par] for checked, par in self.parities_touples if checked.get() is True]
            if not parities:
                raise Exception('parities cannot be empty')
            stopbits = [App.STOPBITS_DICT[stop] for checked, stop in self.stopbits_touples if checked.get() is True]
            if not stopbits:
                raise Exception('stopbits cannot be empty')

            bytesizes = [8]

            self.__update_network_time()
            self.app.root.update_idletasks()
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
            self.info_label.config(text='scanning completed succesfully')
        except Exception as e:
            logging.exception(str(e))
            self.info_label.config(text=str(e))

    def __update_device_identification_results(self):
        self.params_label.config(text=f'params: {self.params}')
        self.devices_label.config(text=f'devices: {self.devices_list}')

    def __start_fc_identification(self):
        try: 
            fc_s = [Device.FUNCTION_CODES_DICT[fc] for checked, fc in self.fc_touples if checked.get() is True]
            if not fc_s:
                raise Exception('No FC\'s checked')
            supported_fcs = Scanner.list_supportable_fc_in_device(self.master, int(self.devices_combo.get()), fc_s)
            self.fc_device_id_label.config(text=f'Device ID: {self.devices_combo.get()}')
            self.supported_fc_label.config(text=f'Supported FCs: {supported_fcs}')
            self.info_label.config(text='scanning completed succesfully')
        except Exception as e:
            logging.exception(str(e))
            self.info_label.config(text=str(e))

    def __start_address_identification(self):
        try:
            data_type_label_dict = {
                'DI': self.address_di_label,
                'Coils': self.address_coils_label,
                'IR': self.address_ir_label,
                'HR': self.address_hr_label
            }

            from_address = int(self.address_from_entry.get())
            to_address = int(self.address_to_entry.get())
            if from_address > to_address:
                raise ValueError('"from" address bigger than "to" address')
            if from_address < 0:
                raise ValueError('"from" address smaller than 0')
            if to_address > int(0xFFFF):
                raise ValueError('"to" address bigger than 247')

            
            data_types = [dt for checked, dt in self.data_types_touples if checked.get() is True]
            
            self.__update_address_time()
            self.app.root.update_idletasks()

            scanning_function = Scanner.list_supportable_addresses_toghether  if self.toghether.get() else Scanner.list_supportable_addresses

            for data_type in data_types:
                addresses = scanning_function(self.master, int(self.address_device_combo.get()), (from_address, to_address), data_type)
                data_type_label_dict[data_type].config(text= f'{data_type} addresses: {addresses}')
            self.address_slave_label.config(text=f'Device ID: {self.address_device_combo.get()}')
            self.info_label.config(text='scanning completed succesfully')

        except Exception as e:
            logging.exception(str(e))
            self.info_label.config(text=str(e))

    def __update_address_time(self, *_event):
        try:
            from_adr = int(self.address_from_entry.get())
            to_adr = int(self.address_to_entry.get())

            data_types = len([dt for checked, dt in self.data_types_touples if checked.get() is True])
      
            if self.toghether.get():
                expected_time = 1
            else: 
                expected_time = floor((to_adr-from_adr)*0.014)*data_types

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
            
            baudrates = len([App.BAUDRATE_DICT[bdr] for checked, bdr in self.baudradrates_touples if checked.get() is True])
            parities = len([App.PARITY_DICT[par] for checked, par in self.parities_touples if checked.get() is True])
            stopbits = len([App.STOPBITS_DICT[stop] for checked, stop in self.stopbits_touples if checked.get() is True])
            bytesizes = 1
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
