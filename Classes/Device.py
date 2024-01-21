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

        left_frame = Frame(self.tab)
        left_frame.pack(side=LEFT)
        self.__create_device_information_frame(left_frame)
        self.__new_task_frame(left_frame)
        self.task_tabs = ttk.Notebook(self.tab)
        self.task_tabs.pack(expand=True, fill='both')
        

    def add_new_task(self, adress = None, length = None, function_code = None):
        if not adress:
            adress = int(self.task_address_entry.get())
        if not function_code:
            function_code = Device.FUNCTION_CODES_DICT[self.function_code_combo.get()]
        if not length:
            if function_code == b'\x05' or function_code == b'\x06':
                length = 1
            else:
                length = int(self.task_length_entry.get()) 

        tab = ttk.Notebook(self.tab)
        tab.pack(expand=1, fill='both')
        self.task_tabs.add(tab, text=str(adress))
        self.tasks.append(Task(self.app, tab, self.address, function_code ,adress, length, self))

    def __create_device_information_frame(self, frame):
        device_information_frame = LabelFrame(frame, text='Device Information:')
        device_information_frame.pack()
        device_address_label = Label(device_information_frame, text=f'Device address: {self.address}')
        device_address_label.pack()
        delete_device_button = Button(device_information_frame, text='Delete Device', command=lambda: self.app.connection.delete_device(self))
        delete_device_button.pack(pady=5)

    def __new_task_frame(self, frame):
        
        new_task_frame = LabelFrame(frame, text='New Task')
        new_task_frame.pack(padx=5, pady=10)
        self.function_code_combo = ttk.Combobox(new_task_frame, values=Device.FUNCTION_CODES)
        self.function_code_combo.current(0)
        self.function_code_combo.pack()
        self.function_code_combo.bind('<<ComboboxSelected>>', self.update_length_entry)
        self.task_address_entry = Entry(new_task_frame)
        self.task_address_entry.pack(pady=(10, 1))
        task_address_label = Label(new_task_frame, text='starting adress')
        task_address_label.pack()
        self.task_length_entry = Entry(new_task_frame, disabledbackground='lightgrey')
        self.task_length_entry.pack(pady=(10, 1))
        task_length_label = Label(new_task_frame, text='length')
        task_length_label.pack()
        new_task_button = Button(new_task_frame, text='New task', command= self.add_new_task)
        new_task_button.pack()

    def update_length_entry(self, *_event):
        fc = self.function_code_combo.get()[0:2]
        if fc == '05' or fc == '06':
            self.task_length_entry.config(state='disabled')
        else:
            self.task_length_entry.config(state='normal')

    def destroy(self):
        for task in self.tasks:
            task.destroy()

    def delete_task(self, task: Task):
        self.tasks.remove(task)
        task.destroy()
        task.tab.destroy()
  