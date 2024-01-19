from __future__ import annotations
from tkinter import *
from tkinter import ttk
import logging
from .Task import Task
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .App import App

class Device:
    
    FUNCTION_CODES = [
        '01: Read Coils',
        '02: Read Discrete Inputs',
        '03: Read Multiple Holding Registers',
        '04: Read Input Registers',
        '05: Write Single Coil',
        '06: Write Single Holding Register',
        '15: Write Multiple Coils',
        '16: Write Multiple Holding Registers'
        ]
        
    FUNCTION_CODES_DICT = {
        '01: Read Coils': b'\x01',
        '02: Read Discrete Inputs': b'\x02',
        '03: Read Multiple Holding Registers': b'\x03',
        '04: Read Input Registers': b'\x04',
        '05: Write Single Coil': b'\x05',
        '06: Write Single Holding Register': b'\x06',
        '15: Write Multiple Coils': b'\x0F',
        '16: Write Multiple Holding Registers': b'\x10'
        }
    
    def __init__(self, app: App, tab, address):
        logging.log(logging.DEBUG, f'Device {address} created')
        self.app = app
        self.tab = tab
        self.address = address
        self.tasks: list[Task] = []

        self.__temp_new_task_frame()
        self.task_tabs = ttk.Notebook(self.tab)
        self.task_tabs.pack(expand=True, fill='both')
        

    def add_new_task(self, adress = None, length = None, function_code = None):
        if not adress:
            adress = int(self.task_address_entry.get())
        if not length:
            length = int(self.task_length_entry.get()) 
        if not function_code:
            function_code = Device.FUNCTION_CODES_DICT[self.function_code_combo.get()]

        tab = ttk.Notebook(self.tab)
        tab.pack(expand=1, fill='both')
        self.task_tabs.add(tab, text=str(adress))
        self.tasks.append(Task(self.app, tab, self.address, function_code ,adress, length))

    def __temp_new_task_frame(self):
        
        new_task_frame = Frame(self.tab)
        new_task_frame.pack(side=LEFT)
        new_task_button = Button(new_task_frame, text='new task', command= self.add_new_task)
        new_task_button.pack()
        self.function_code_combo = ttk.Combobox(new_task_frame, values=Device.FUNCTION_CODES)
        self.function_code_combo.current(0)
        self.function_code_combo.pack()
        self.task_address_entry = Entry(new_task_frame)
        self.task_address_entry.pack(pady=(10, 1))
        task_address_label = Label(new_task_frame, text='starting adress')
        task_address_label.pack()
        self.task_length_entry = Entry(new_task_frame)
        self.task_length_entry.pack(pady=(10, 1))
        task_length_label = Label(new_task_frame, text='length')
        task_length_label.pack()
  