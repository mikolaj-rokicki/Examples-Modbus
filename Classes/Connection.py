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
