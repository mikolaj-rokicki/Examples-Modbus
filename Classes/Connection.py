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
        new_device_button = Button(self.window, text='new device', command= self.add_new_device)
        new_device_button.pack()
        self.device_address_entry = Entry(self.window)
        self.device_address_entry.pack(pady=(10, 1))
        device_address_label = Label(self.window, text='device adress')
        device_address_label.pack()
        self.device_tabs = ttk.Notebook(self.window)
        self.device_tabs.pack(expand=True, fill='both')

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

