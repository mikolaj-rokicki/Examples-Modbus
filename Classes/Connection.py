from tkinter import *
from tkinter import ttk
import logging
from .Device import Device
from typing import TYPE_CHECKING




class Connection:
    def __init__(self, app, window, params):
        logging.log(logging.DEBUG, 'Connection created')
        self.app = app
        self.window = window
        self.devices: list[Device] = []
        if type(params) is list:
            self.params = {
                'port_no': params[0],
                'baudrate': params[1],
                'parity': params[2],
                'stopbits': params[3],
                'bytesize': params[4]
            }
        elif type(params) is dict:
            self.params = params

        connection_settings_frame = Frame(self.window)
        connection_settings_frame.pack()
        self.__create_connection_information_frame(connection_settings_frame)
        self.__create_new_device_frame(connection_settings_frame)

        
        self.device_tabs = ttk.Notebook(self.window)
        self.device_tabs.pack(expand=True, fill='both')

    def __create_new_device_frame(self, frame):
        new_device_frame = LabelFrame(frame, text='New Device')
        new_device_frame.pack(side=LEFT, padx=10)
        new_device_button = Button(new_device_frame, text='Add', command= self.add_new_device)
        new_device_button.pack()
        self.device_address_entry = Entry(new_device_frame)
        self.device_address_entry.pack(pady=(10, 1))
        device_address_label = Label(new_device_frame, text='device adress')
        device_address_label.pack()

    def __create_connection_information_frame(self, frame):
        
        connection_frame = LabelFrame(frame, text='Connection Information')
        connection_frame.pack(side=LEFT)
        port_no_label = Label(connection_frame, text=f'COM Port: {self.params["port_no"]}', anchor='w')
        port_no_label.pack()
        baudrate_label = Label(connection_frame, text=f'Baudrate: {self.params["baudrate"]}', anchor='w')
        baudrate_label.pack()
        parity_label = Label(connection_frame, text=f'Parity: {self.params["parity"]}', anchor='w')
        parity_label.pack()
        stopbits_label = Label(connection_frame, text=f'Stopbits: {self.params["stopbits"]}', anchor='w')
        stopbits_label.pack()
        bytesize_label = Label(connection_frame, text=f'Bytesize: {self.params["bytesize"]}', anchor='w')
        bytesize_label.pack()

    def add_new_device(self, adress = None):
        self.app.devices_menu.entryconfig('Delete Devices', state=NORMAL)
        if not adress:
            adress = int(self.device_address_entry.get()) 
        tab = ttk.Notebook(self.window)
        tab.pack(expand=1, fill='both')
        self.device_tabs.add(tab, text=str(adress))
        device = Device(self.app, tab, adress)
        self.devices.append(device)
        return device
    
    def delete_device(self, device: Device):
        self.devices.remove(device)
        device.tab.destroy()
        device.destroy()


    def delete_devices(self):
        for device in self.devices:
            device.tab.destroy()
        self.devices = []
        self.app.devices_menu.entryconfig('Delete Devices', state=DISABLED)

    def change_connection(self, master, port_no = None, baudrate = None, parity = None, stopbits = None, bytesize = None):
        if not (port_no or baudrate or parity or stopbits or bytesize):
            logging.warning('connection parameters haven\'t changed')
            return
        if port_no == self.params['port_no'] and baudrate == self.params['baudrate'] and parity == self.params['parity'] and stopbits == self.params['stopbits'] and bytesize == self.params['bytesize']:
            logging.warning('connection parameters haven\'t changed')
            return
        logging.log(logging.DEBUG, 'Connection changed')
        if port_no:
            self.params['port_no'] = port_no
        if baudrate:
            self.params['baudrate'] = baudrate
        if parity:
            self.params['parity'] = parity
        if stopbits:
            self.params['stopbits'] = stopbits
        if bytesize:
            self.params['bytesize'] = bytesize
        for device in self.devices:
            for task in device.tasks:
                task.master = master
        
    def destroy(self):
        for device in self.devices:
            device.destroy()
        self.window.destroy()
        self.app.devices_menu.entryconfig('Delete Devices', state=DISABLED)

