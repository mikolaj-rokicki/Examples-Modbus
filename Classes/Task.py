from __future__ import annotations
from tkinter import *
from tkinter import ttk
import math
from random import randint
from enum import Enum
import logging
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .App import App


class Task:
    
    class Data_Types(Enum):
        Digital = 1
        Registers = 2

    class Transmission_Types(Enum):
        Read = 1
        Write = 2

    DATA_TYPE_DICT = {
        b'\x01': Data_Types.Digital,
        b'\x02': Data_Types.Digital,
        b'\x03': Data_Types.Registers,
        b'\x04': Data_Types.Registers,
        b'\x05': Data_Types.Digital,
        b'\x06': Data_Types.Registers,
        b'\x0F': Data_Types.Digital,
        b'\x10': Data_Types.Registers
        }
    
    TRANSMISSION_TYPE_DICT = {
        b'\x01': Transmission_Types.Read,
        b'\x02': Transmission_Types.Read,
        b'\x03': Transmission_Types.Read,
        b'\x04': Transmission_Types.Read,
        b'\x05': Transmission_Types.Write,
        b'\x06': Transmission_Types.Write,
        b'\x0F': Transmission_Types.Write,
        b'\x10': Transmission_Types.Write
        }
    
    
    def __init__(self, app: App, tab, device_id, function_code, starting_adress, length, device) -> None:
        
        self.app = app
        self.tab = tab
        self.device_id = device_id
        self.function_code = function_code
        self.starting_adress = starting_adress
        self.length = length
        self.device = device

        self.root = app.root
        self.master = app.master

        self.data_type = Task.DATA_TYPE_DICT[function_code]
        self.transmission_type = Task.TRANSMISSION_TYPE_DICT[function_code]

        top_frame = Frame(tab)
        top_frame.pack(side=TOP)

        self.info_frame = Frame(tab)
        self.info_frame.pack(side=BOTTOM, fill='x', expand=1)
        self.info_label = Label(self.info_frame, text='ready', anchor=E, padx=10)
        self.info_label.pack(side=BOTTOM, expand=1, fill=X)
        self.root.after(15, lambda: self.info_label.config(width=self.root.winfo_width()))


        self.__create_task_information(top_frame)
        self.__create_task_settings(top_frame)

        self.table_frame = Frame(tab)
        self.table_frame.pack(fill='both', expand=1)

        self.__create_table(self.starting_adress, self.length)

    def __create_task_information(self, frame):
        task_information_frame = LabelFrame(frame, text='task information')
        task_information_frame.pack(side=LEFT)
        function_code_label = Label(task_information_frame, text=f'Function Code: {self.function_code}')
        function_code_label.pack()
        first_address_label = Label(task_information_frame, text=f'First Address: {self.starting_adress}')
        first_address_label.pack()
        length_label = Label(task_information_frame, text=f'Length: {self.length}')
        length_label.pack()
        delete_task_button = Button(task_information_frame, text='Delete Task', command=lambda: self.device.delete_task(self))
        delete_task_button.pack()

    def __create_task_settings(self, frame):
        task_settings_frame = LabelFrame(frame, text='task settings')
        task_settings_frame.pack(side=LEFT, padx=10)
        self.__create_display_settings(task_settings_frame)
        self.__create_update_settings(task_settings_frame)

    def __create_display_settings(self, task_settings_frame):
        DISPLAY_TYPES_REGISTERS = ['Integer','Hexadecimal', 'Binary', 'ASCII']
        DISPLAY_TYPES_COILS = ['True/False', '0/1']
        display_type_frame = LabelFrame(task_settings_frame, text='Display Settings')
        display_type_frame.pack(side=LEFT)
        if self.data_type is Task.Data_Types.Digital:
            self.display_type_combo = ttk.Combobox(display_type_frame, values = DISPLAY_TYPES_COILS)
        else:
            self.display_type_combo = ttk.Combobox(display_type_frame, values = DISPLAY_TYPES_REGISTERS)
        self.display_type_combo.current(0)
        self.display_type = self.display_type_combo.get()
        self.display_type_combo.pack(padx=5, pady=5)
        self.display_type_combo.bind('<<ComboboxSelected>>', self.__update_display_type)

    def __create_update_settings(self, task_settings_frame):
        update_settings_frame = LabelFrame(task_settings_frame, text='Update settings')
        update_settings_frame.pack(side=LEFT, padx=10)
        self.auto_refresh = BooleanVar(value=False)
        auto_refresh_checkbutton = Checkbutton(update_settings_frame, text='Auto-Refresh', variable=self.auto_refresh, command=self.__update_auto_refresh)
        auto_refresh_checkbutton.pack()
        auto_refresh_rate_frame = Frame(update_settings_frame)
        auto_refresh_rate_frame.pack()
        auto_refresh_rate_label1 = Label(auto_refresh_rate_frame, text='rate')
        auto_refresh_rate_label1.pack(side= LEFT)
        self.auto_refresh_rate_entry = Entry(auto_refresh_rate_frame, disabledbackground='lightgray')
        self.auto_refresh_rate_entry.insert(0, str(1000))
        self.auto_refresh_rate_entry.pack(side=LEFT)
        self.auto_refresh_rate_entry.bind('<Return>', self.__update_auto_refresh)
        self.auto_refresh_rate = int(self.auto_refresh_rate_entry.get())
        auto_refresh_rate_label2 = Label(auto_refresh_rate_frame, text='ms')
        auto_refresh_rate_label2.pack(side=LEFT)
        if self.transmission_type is Task.Transmission_Types.Read:
            self.auto_refresh_button = Button(update_settings_frame, text='update', command= lambda: self.__update_values_read())
        else:
            self.auto_refresh_button = Button(update_settings_frame, text='update', command= lambda: self.__update_values_write())
        self.auto_refresh_button.pack()
        self.__update_auto_refresh()

    def __update_auto_refresh(self, *_event):
        try:
            auto_refresh = self.auto_refresh.get()
            self.auto_refresh_button.config(state='disabled' if auto_refresh else 'normal')
            self.auto_refresh_rate_entry.config(state='normal' if auto_refresh else 'disabled')
            if hasattr(self, 'update_values_task'):
                self.root.after_cancel(self.update_values_task)
            if auto_refresh:
                self.auto_refresh_rate = int(self.auto_refresh_rate_entry.get())
                if self.auto_refresh_rate < 100:
                    raise ValueError('refresh rate cannot be highier than 10/s')
                if self.transmission_type is Task.Transmission_Types.Read:
                    self.__update_values_read(self.auto_refresh_rate)
                else:
                    self.__update_values_write(self.auto_refresh_rate)
        except Exception as e:
            self.info_label.config(text=str(e))

    def __update_display_type(self, *_event):
        self.display_type = self.display_type_combo.get()
        old_info = self.info_label.cget('text')
        self.info_label.config(text='display type updated')
        self.__refresh_values()
        self.root.after(500, lambda: self.info_label.config(text=old_info))

    def __create_table(self, starting_adress, length):

        self.table_left_frame = Frame(self.table_frame)
        self.table_left_frame.pack(side=LEFT, fill=Y, padx=(10, 0))
        self.table_left = Frame(self.table_left_frame)
        self.table_left.pack(side=TOP)

        self.canvas = Canvas(self.table_frame, height=300, scrollregion=(0, 0, 5000, 0), highlightthickness=0, background='green')
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        canvas_scroll_bar = Scrollbar(self.canvas, orient=HORIZONTAL, command=self.canvas.xview) 
        canvas_scroll_bar.pack(side=BOTTOM, fill=X)
        self.canvas.config(xscrollcommand=canvas_scroll_bar.set)
        self.table = Frame(self.canvas)
        self.canvas.create_window(0, 0, window=self.table, anchor='nw')
        self.table.bind('<Configure>', self.on_config)

        self.values_length = length
        ROWS = 10
        values_to_skip = starting_adress%10
        columns = 2*math.ceil(self.values_length/ROWS)
        top_left_corner = Label(self.table_left, width=20, background='lightgray', borderwidth=1, relief='solid')
        top_left_corner.grid(column=0, row=0)
        # left column
        left_column = [Label(self.table_left, text=i, width=20, background='lightgray', borderwidth=1, relief='solid') for i in range(0,10)]
        for i in range(0, ROWS):
            left_column[i].grid(column=0, row=i+1)
        # top row
        top_row = [Label(self.table, text= 'alias' if i%2==0 else f'{int(((i-1)/2)*ROWS)+math.floor(starting_adress/10)}', width=20, background='lightgray', borderwidth=1, relief='solid') for i in range(0, columns)]
        for j in range(0, columns):
            top_row[j].grid(column=j, row=0)
        # aliases
        for i in range(0, ROWS):
            for j in range(0, int(columns/2)):
                e = Entry(self.table, width=20, disabledbackground='lightgray', state=DISABLED if i+j*ROWS+1>self.values_length+values_to_skip or (j==0 and i<values_to_skip) else NORMAL)
                e.grid(column=j*2, row=i+1)
        # values
        self.values_entry: list[Entry] = [] 
        entry_state = 'readonly' if self.transmission_type is Task.Transmission_Types.Read else 'normal'
        for j in range(0, int(columns/2)):
            for i in range(0, ROWS):
                e = Entry(self.table, width=20, disabledbackground='lightgray', state='disabled' if i+j*ROWS+1>self.values_length+values_to_skip or (j==0 and i<values_to_skip) else entry_state)
                if e['state'] !='disabled':
                    self.values_entry.append(e)
                if entry_state == 'normal':
                    e.bind('<Return>', self.__update_values_write)
                e.grid(column=j*2+1, row=i+1)

    def __update_values_read(self, *args):
        
        if self.app.WINDOWS:
            if self.data_type is Task.Data_Types.Digital:
                self.values = [bool(randint(0, 1)) for _ in range(0, len(self.values_entry))]
            else:
                self.values = [randint(0, int(0xFFFF)) for _ in range(0, len(self.values_entry))]
        else:
            self.__pool_values()
        if self.data_type is Task.Data_Types.Registers:
            for i, value in enumerate(self.values_entry, start=0):
                if i<self.values_length:
                    value.configure(state=NORMAL)
                    value.delete(0, END)
                    if self.display_type == 'Integer':
                        value.insert(0, str(self.values[i]))
                    elif self.display_type == 'Binary':
                        value.insert(0, str(bin(self.values[i])[2:]).zfill(16))
                    elif self.display_type == 'Hexadecimal':
                        value.insert(0, str(hex(self.values[i])[2:]).zfill(4).upper())
                    elif self.display_type == 'ASCII':
                        value.insert(0, str(chr(self.values[i])))
                    value.configure(state='readonly')
        else:
            for i, value in enumerate(self.values_entry, start=0):
                if i<self.values_length:
                    value.configure(state=NORMAL)
                    value.delete(0, END)
                    if self.display_type == 'True/False':
                        value.insert(0, 'True' if self.values[i] else 'False')
                    elif self.display_type == '0/1':
                        value.insert(0, str(bin(self.values[i])[2:]).zfill(1))
                    value.configure(state='readonly')
        if args:
            self.update_values_task = self.root.after(args[0], lambda: self.__update_values_read(args[0]))

    def __update_values_write(self, *args):

        if self.data_type is Task.Data_Types.Registers:
            if self.display_type == 'Integer':
                self.values = [int(entry.get()) for entry in self.values_entry]
            elif self.display_type == 'Binary':
                self.values = [int(entry.get(), 2) for entry in self.values_entry]
            elif self.display_type == 'Hexadecimal':
                self.values = [int(entry.get(), 16) for entry in self.values_entry]
            elif self.display_type == 'ASCII':
                self.values = [ord(entry.get()) for entry in self.values_entry]
        else:
            if self.display_type == 'True/False':
                self.values = [entry.get().lower() not in ('false', '0', '') for entry in self.values_entry]
            elif self.display_type == '0/1':
                self.values = [bool(int(entry.get())) for entry in self.values_entry]
        self.__push_values()
        if args:
            if type(args) is int:
                self.update_values_task = self.root.after(args[0], lambda: self.__update_values_write(args[0]))

    def __refresh_values(self):
        if hasattr(self, 'values'):
            entry_state = 'readonly' if self.transmission_type is Task.Transmission_Types.Read else 'normal'
            if self.data_type is Task.Data_Types.Registers:
                for i, value in enumerate(self.values_entry, start=0):
                    if i<self.values_length:
                        value.configure(state=NORMAL)
                        value.delete(0, END)
                        if self.display_type == 'Integer':
                            value.insert(0, str(self.values[i]))
                        elif self.display_type == 'Binary':
                            value.insert(0, str(bin(self.values[i])[2:]).zfill(16))
                        elif self.display_type == 'Hexadecimal':
                            value.insert(0, str(hex(self.values[i])[2:]).zfill(4).upper())
                        elif self.display_type == 'ASCII':
                            value.insert(0, str(chr(self.values[i])))
                        value.configure(state=entry_state)
            else:
                for i, value in enumerate(self.values_entry, start=0):
                    if i<self.values_length:
                        value.configure(state=NORMAL)
                        value.delete(0, END)
                        if self.display_type == 'True/False':
                            value.insert(0, 'True' if self.values[i] else 'False')
                        elif self.display_type == '0/1':
                            value.insert(0, str(bin(self.values[i])[2:]).zfill(1))
                        value.configure(state=entry_state)

    def on_config(self, e):
        self.canvas.configure(scrollregion=(0, 0, e.width+20, e.height+20))
        logging.debug(f'new canvas borders: {0, 0, e.width+20, e.height+20}')

    def __update_display_type(self, *_event):
        logging.debug('display type updated')
        self.display_type = self.display_type_combo.get()
        old_info = self.info_label.cget('text')
        self.info_label.config(text='display type updated')
        self.__refresh_values()
        self.root.after(500, lambda: self.info_label.config(text=old_info))

    def __pool_values(self):
        if self.function_code == b'\x01':
            self.values = self.master.read_discrete_inputs(self.device_id, self.starting_adress, self.length)
        elif self.function_code == b'\x02':
            self.values = self.master.read_coils(self.device_id, self.starting_adress, self.length)
        elif self.function_code == b'\x03':
            self.values = self.master.read_multiple_holding_registers(self.device_id, self.starting_adress, self.length)
        elif self.function_code == b'\x04':
            self.values = self.master.read_input_registers(self.device_id, self.starting_adress, self.length)
        
    def __push_values(self):
        if self.function_code == b'\x05':
            self.master.write_single_coil(self.device_id, self.starting_adress, self.values[0])
            logging.info(f'write single coil - device id: {self.device_id}, starting address: {self.starting_adress}, value: {self.values[0]}')
        elif self.function_code == b'\x06':
            self.master.write_single_holding_register(self.device_id, self.starting_adress, self.values[0])
            logging.info(f'write single HR - device id: {self.device_id}, starting address: {self.starting_adress}, value: {self.values[0]}')
        elif self.function_code == b'\x0F':
            self.master.write_multiple_coils(self.device_id, self.starting_adress, self.values)
            logging.info(f'write multiple coils - device id: {self.device_id}, starting address: {self.starting_adress}, values: {self.values}')
        elif self.function_code == b'\x10':
            self.master.write_multiple_holding_registers(self.device_id, self.starting_adress, self.values)
            logging.info(f'write multiple HR - device id: {self.device_id}, starting address: {self.starting_adress}, values: {self.values}')
        else:
            raise Exception(f'function code {self.function_code} not supporter por push values')
        
    def destroy(self):
        if hasattr(self, 'update_values_task'):
                self.root.after_cancel(self.update_values_task)
