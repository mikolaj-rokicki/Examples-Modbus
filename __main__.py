from tkinter import *
import customtkinter
from tkinter import ttk
import math
from typing import Literal
from CM4_MBUS_LIB import RS485_RTU_Master
import serial
from random import randint
from enum import Enum

class App:

    def __init__(self):
        self.root = Tk()
        self.root.title('Modbus Master')
        self.root.geometry('900x480')
        #self.table_scroll = Scrollbar(self.root, orient=HORIZONTAL)
        #self.table_scroll.pack(side=BOTTOM, fill=X)
        self.__create_menu()
        self.info_label = Label(self.root, text='Establish Connection First', anchor=E, padx=10)
        if SKIP_CONNECTION:
            self.root.after(10, lambda: self.__create_fc_tab())
        self.info_label.pack(side=BOTTOM)
        self.root.after(1, lambda: self.info_label.config(width=self.root.winfo_width()))
        if SKIP_TO_TABLE:
            if not SKIP_CONNECTION:
                self.root.after(10, lambda: self.__create_fc_tab())  
            self.root.after(15, lambda: self.__create_settings([True, True, b'\x10']))
            self.root.after(20, lambda: self.__create_table(13, 14))
            self.root.after(20, lambda: self.__create_update_settings())
        self.root.after(1000, lambda: self.__temp_every_second())
        self.root.mainloop()

    def __create_menu(self):
        self.my_menu = Menu(self.root)
        self.root.config(menu=self.my_menu)
        self.connection_menu = Menu(self.my_menu, tearoff=False)
        self.my_menu.add_cascade(label='Connections', menu=self.connection_menu)
        self.connection_menu.add_command(label='Create Connection', command= lambda: self.__create_connection_tab())
        self.connection_menu.add_command(label= 'Delete Connection', command= lambda: self.__delete_settings(), state=DISABLED)
        
    def __create_connection_tab(self):
        conn = Toplevel(self.root)
        conn.title('Create Connection')
        conn.geometry('400x400')
        conn.grab_set()
        COMS = ['COM0', 'COM1', 'COM2', 'COM3', 'NONE'] # TODO: delete None
        BAUDRATES = ['19200']
        PARITIES = ['NONE']
        STOPBITS = ['ONE', 'TWO']
        BYTESIZE = ['8 bits', '5 bits']
        com_frame = Frame(conn, width=600, height=600)
        com_frame.pack()
        com_label = customtkinter.CTkLabel(com_frame, text='COM Port')
        com_label.pack()
        com_combo = customtkinter.CTkComboBox(com_frame, values=COMS)
        com_combo.pack()
        bdr_frame = Frame(conn)
        bdr_frame.pack()
        bdr_label = customtkinter.CTkLabel(bdr_frame, text='Baudrate')
        bdr_label.pack()
        bdr_combo = customtkinter.CTkComboBox(bdr_frame, values=BAUDRATES)
        bdr_combo.pack()
        parity_frame = Frame(conn)
        parity_frame.pack()
        parity_label = customtkinter.CTkLabel(parity_frame, text='Parity Bits')
        parity_label.pack()
        parity_combo = customtkinter.CTkComboBox(parity_frame, values=PARITIES)
        parity_combo.pack()
        stopbits_frame = Frame(conn)
        stopbits_frame.pack()
        stopbits_label = customtkinter.CTkLabel(stopbits_frame, text='Stop Bits')
        stopbits_label.pack()
        stopbits_combo = customtkinter.CTkComboBox(stopbits_frame, values=STOPBITS)
        stopbits_combo.pack()
        bytesize_frame = Frame(conn)
        bytesize_frame.pack()
        bytesize_label = customtkinter.CTkLabel(bytesize_frame, text='Bytesize')
        bytesize_label.pack()
        bytesize_combo = customtkinter.CTkComboBox(bytesize_frame, values=BYTESIZE)
        bytesize_combo.pack()
        info_frame = customtkinter.CTkFrame(conn, width=400)
        info_frame.pack(side = BOTTOM)
        self.conn_info_label = Label(info_frame, text='ready', anchor=E, padx=10)
        self.conn_info_label.pack(side = LEFT)
        conn.after(10, lambda: self.conn_info_label.config(width = conn.winfo_width()))
        create_button = customtkinter.CTkButton(conn, text='Create Connection', 
                                                command= lambda: self.__create_connection(conn, 
                                                                                          com_combo.get(), 
                                                                                          bdr_combo.get(), 
                                                                                          parity_combo.get(), 
                                                                                          stopbits_combo.get(), 
                                                                                          bytesize_combo.get()
                                                                                          )
                                                )
        create_button.pack(pady = 10)

        conn.mainloop()

    def __create_connection(self, conn: Tk, port_no, baudrate, parity, stopbits, bytesize):
        COMS_DICT = {
            'COM0': 0,
            'COM1': 1,
            'COM2': 2,
            'COM3': 3,
            'NONE': None
        }        
        BAUDRATE_DICT = {
            '19200': 19200
        }
        PARITY_DICT = {
            'NONE': serial.PARITY_NONE
        }
        STOPBITS_DICT = {
            'ONE': serial.STOPBITS_ONE,
            'TWO': serial.STOPBITS_TWO
        }
        BYTESIZE_DICT = {
            '8 bits': serial.EIGHTBITS,
            '5 bits': serial.FIVEBITS
        }
        try:
            self.master = RS485_RTU_Master.RS485_RTU_Master(COMS_DICT[port_no], 
                                                            baudrate=BAUDRATE_DICT[baudrate], 
                                                            parity=PARITY_DICT[parity], 
                                                            stopbits=STOPBITS_DICT[stopbits], 
                                                            bytesize=BYTESIZE_DICT[bytesize]
                                                            )
        except Exception as e:
            self.conn_info_label.configure(text = str(e))
            return
        conn.grab_release()
        self.__create_fc_tab()
        self.connection_menu.entryconfig('Create Connection', state=DISABLED)
        conn.destroy()

    def __create_fc_tab(self):
        self.info_label.config(text='Choose function code')
        self.settings_frame = Frame(self.root)
        self.settings_frame.pack()
        function_code_frame = LabelFrame(self.settings_frame, text='Function Code')
        function_code_frame.pack(side=LEFT)
        FUNCTION_CODES = ['01: Read Coils',
                          '02: Read Discrete Inputs',
                          '03: Read Multiple Holding Registers',
                          '04: Read Input Registers',
                          '05: Write Single Coil',
                          '06: Write Single Holding Register',
                          '15: Write Multiple Coils',
                          '16: Write Multiple Holding Registers']
        
        FUNCTION_CODES_DICT = {
            '01: Read Coils': [True, False, b'\x01'], # length, writtable
            '02: Read Discrete Inputs': [True, False, b'\x02'],
            '03: Read Multiple Holding Registers': [True, False, b'\x03'],
            '04: Read Input Registers': [True, False, b'\x04'],
            '05: Write Single Coil': [False, True, b'\x05'],
            '06: Write Single Holding Register': [False, True, b'\x06'],
            '15: Write Multiple Coils': [True, True, b'\x0F'],
            '16: Write Multiple Holding Registers': [True, True, b'\x10']
        }
        function_code_combo = ttk.Combobox(function_code_frame, values=FUNCTION_CODES)
        function_code_combo.set(FUNCTION_CODES[0])
        function_code_combo.pack()
        confirm_button = Button(function_code_frame, text='Ok', command= lambda: self.__create_settings(FUNCTION_CODES_DICT[function_code_combo.get()]))
        confirm_button.pack()
        self.connection_menu.entryconfig('Delete Connection', state=NORMAL)

    class Data_Types(Enum):
        Digital = 1
        Registers = 2

    class Transmission_Types(Enum):
        Read = 1
        Write = 2

    def __assign_function_code(self, params):
        DATA_TYPE_DICT = {
            b'\x01': App.Data_Types.Digital,
            b'\x02': App.Data_Types.Digital,
            b'\x03': App.Data_Types.Registers,
            b'\x04': App.Data_Types.Registers,
            b'\x05': App.Data_Types.Digital,
            b'\x06': App.Data_Types.Registers,
            b'\x0F': App.Data_Types.Digital,
            b'\x10': App.Data_Types.Registers
        }
        TRANSMISSION_TYPE_DICT = {
            b'\x01': App.Transmission_Types.Read,
            b'\x02': App.Transmission_Types.Read,
            b'\x03': App.Transmission_Types.Read,
            b'\x04': App.Transmission_Types.Read,
            b'\x05': App.Transmission_Types.Write,
            b'\x06': App.Transmission_Types.Write,
            b'\x0F': App.Transmission_Types.Write,
            b'\x10': App.Transmission_Types.Write
        }
        self.function_code = params[2]
        self.data_type = DATA_TYPE_DICT[self.function_code]
        self.transmission_type = TRANSMISSION_TYPE_DICT[self.function_code]

    def __create_settings(self, params):
        self.__assign_function_code(params)
        self.__delete_update_settings()
        self.__delete_table_canvas()
        self.info_label.config(text='Configure input parameters')
        if hasattr(self, 'device_settings_frame'):
            self.device_settings_frame.destroy()
        if hasattr(self, 'display_settings_frame'):
            self.display_settings_frame.destroy()
        self.device_settings_frame = LabelFrame(self.settings_frame, text='Device Settings', padx=5, pady=5)
        self.device_settings_frame.pack(side=LEFT, padx=10)
        device_settings_frame_top = Frame(self.device_settings_frame)
        device_settings_frame_top.pack()
        device_settings_frame_bottom = Frame(self.device_settings_frame)
        device_settings_frame_bottom.pack()
        device_ID_label = Label(device_settings_frame_top, text='Device ID')
        device_ID_label.pack(side=LEFT)
        device_ID_box = Entry(device_settings_frame_top, width=20)
        device_ID_box.pack(side=LEFT)
        adress_label = Label(device_settings_frame_top, text='Adress')
        adress_label.pack(side=LEFT)
        adress_box = Entry(device_settings_frame_top, width=20)
        adress_box.pack(side=LEFT)
        if params[0]:
            length_label = Label(device_settings_frame_bottom, text='Length')
            length_label.pack(side=LEFT)
            length_box = Entry(device_settings_frame_bottom, width=20)
            length_box.pack(side=LEFT)
            length = length_box.get
        else:
            length = 1
        confirm_button = Button(device_settings_frame_bottom, text='OK', command=lambda: self.__update_device(device_ID_box.get(), adress_box.get(), length, params[1]))
        confirm_button.pack(side=LEFT)

        self.display_settings_frame = LabelFrame(self.settings_frame, text='Display Settings')
        self.display_settings_frame.pack(side=LEFT)
        
        DISPLAY_TYPES_REGISTERS = ['ASCII', 'Integer','Hexadecimal', 'Binary']
        DISPLAY_TYPES_COILS = ['True/False', '0/1']
        display_type_label = Label(self.display_settings_frame, text='Display Type')
        display_type_label.pack()
        if self.data_type is App.Data_Types.Digital:
            self.display_type_combo = ttk.Combobox(self.display_settings_frame, values = DISPLAY_TYPES_COILS)
        else:
            self.display_type_combo = ttk.Combobox(self.display_settings_frame, values = DISPLAY_TYPES_REGISTERS)
        self.display_type_combo.current(0)
        self.display_type = self.display_type_combo.get()
        self.display_type_combo.pack(padx=5, pady=5)
        self.display_type_combo.bind('<<ComboboxSelected>>', self.__update_display_type)
        confirm_button.pack()
        self.__create_update_settings()
    
    def __delete_settings(self):
        self.settings_frame.destroy()
        self.connection_menu.entryconfig('Create Connection', state=NORMAL)
        self.__delete_table_canvas()
        self.connection_menu.entryconfig('Delete Connection', state=DISABLED)

    def __update_display_type(self, *_event):
        self.display_type = self.display_type_combo.get()
        old_info = self.info_label.cget('text')
        self.info_label.config(text='display type updated')
        self.__refresh_values()
        self.root.after(500, lambda: self.info_label.config(text=old_info))

    def __pool_values(self):
        if self.function_code == b'\x01':
            self.values = self.master.read_discrete_inputs(self.device_ID, self.starting_adress, self.length)
        elif self.function_code == b'\x02':
            self.values = self.master.read_coils(self.device_ID, self.starting_adress, self.length)
        elif self.function_code == b'\x03':
            self.values = self.master.read_multiple_holding_registers(self.device_ID, self.starting_adress, self.length)
        elif self.function_code == b'\x04':
            self.values = self.master.read_input_registers(self.device_ID, self.starting_adress, self.length)
        
    def __push_values(self):
        if self.function_code == b'\x05':
            self.master.write_single_coil(self.device_ID, self.starting_adress, self.values[0])
        elif self.function_code == b'\x06':
            self.master.write_single_holding_register(self.device_ID, self.starting_adress, self.values[0])
        elif self.function_code == b'\x0F':
            self.master.write_multiple_coils(self.device_ID, self.starting_adress, self.values)
        elif self.function_code == b'\x10':
            self.master.write_multiple_holding_registers(self.device_ID, self.starting_adress, self.values)
        print('values pushed')

    def __refresh_values(self):
        if hasattr(self, 'values'):
            entry_state = 'readonly' if self.transmission_type is App.Transmission_Types.Read else 'normal'
            if self.data_type is App.Data_Types.Registers:
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

    def __update_values_write(self, *args):

        if self.data_type is App.Data_Types.Registers:
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


    def __update_values_read(self, *args):
        
        if WINDOWS:
            if self.data_type is App.Data_Types.Digital:
                self.values = [bool(randint(0, 1)) for _ in range(0, len(self.values_entry))]
            else:
                self.values = [randint(0, int(0xFFFF)) for _ in range(0, len(self.values_entry))]
        else:
            self.__pool_values()
        if self.data_type is App.Data_Types.Registers:
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

    def __update_device(self, device_ID: str, adress: str, length, writtable: bool):
        try:
            self.device_ID = int(device_ID)
            self.starting_adress = int(adress)
            if callable(length):
                self.length = int(length())
            else:
                self.length = length
            self.__create_table(self.starting_adress, self.length)
            
        except Exception as e:
            self.info_label.config(text=str(e))

    def __delete_update_settings(self):
        if hasattr(self, 'update_settings_frame'):
            self.update_settings_frame.destroy()

    def __update_auto_refresh(self, *_event):
        auto_refresh = self.auto_refresh.get()
        self.auto_refresh_button.config(state='disabled' if auto_refresh else 'normal')
        self.auto_refresh_rate_entry.config(state='normal' if auto_refresh else 'disabled')
        if auto_refresh:
            self.auto_refresh_rate = int(self.auto_refresh_rate_entry.get())
            if hasattr(self, 'update_values_task'):
                self.root.after_cancel(self.update_values_task)
            if self.transmission_type is App.Transmission_Types.Read:
                self.__update_values_read(self.auto_refresh_rate)
            else:
                self.__update_values_write(self.auto_refresh_rate)


    def __create_update_settings(self):
        self.__delete_update_settings()
        self.update_settings_frame = LabelFrame(self.settings_frame, text='Update settings')
        self.update_settings_frame.pack(side=LEFT, padx=10)
        self.auto_refresh = BooleanVar(value=False)
        auto_refresh_checkbutton = Checkbutton(self.update_settings_frame, text='Auto-Refresh', variable=self.auto_refresh, command=self.__update_auto_refresh)
        auto_refresh_checkbutton.pack()
        auto_refresh_rate_frame = Frame(self.update_settings_frame)
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
        if self.transmission_type is App.Transmission_Types.Read:
            self.auto_refresh_button = Button(self.update_settings_frame, text='update', command= lambda: self.__update_values_read())
        else:
            self.auto_refresh_button = Button(self.update_settings_frame, text='update', command= lambda: self.__update_values_write())
        self.auto_refresh_button.pack()
        self.__update_auto_refresh()

    def __temp_every_second(self):
        #print(self.auto_refresh.get())
        self.root.after(1000, lambda: self.__temp_every_second())

    def __delete_table_canvas(self):
        if hasattr(self, 'canvas'):
            self.canvas.destroy()
        if hasattr(self, 'table_left_frame'):
            self.table_left_frame.destroy()
        if hasattr(self, 'update_values_task'):
            self.root.after_cancel(self.update_values_task)

    def __update_canvas_borders(self):
        self.canvas.config(scrollregion=(0, 0, self.table.winfo_reqwidth()+20, self.table.winfo_reqheight()+20))

    def __create_table(self, starting_adress, length):
        self.__delete_table_canvas()
        self.table_left_frame = Frame(self.root)
        self.table_left_frame.pack(side=LEFT, fill=Y, padx=(10, 0))
        self.table_left = Frame(self.table_left_frame)
        self.table_left.pack(side=TOP)
        self.canvas = Canvas(self.root, scrollregion=(0, 0, 10000, 1000), highlightthickness=0)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        canvas_scroll_bar = Scrollbar(self.canvas, orient=HORIZONTAL, command=self.canvas.xview) 
        canvas_scroll_bar.pack(side=BOTTOM, fill=X)
        self.canvas.config(xscrollcommand=canvas_scroll_bar.set)
        self.table = Frame(self.canvas)
        self.canvas.create_window(0, 0, window=self.table, anchor='nw')
        self.root.after(60, lambda: self.__update_canvas_borders())
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
        entry_state = 'readonly' if self.transmission_type is App.Transmission_Types.Read else 'normal'
        for j in range(0, int(columns/2)):
            for i in range(0, ROWS):
                e = Entry(self.table, width=20, disabledbackground='lightgray', state='disabled' if i+j*ROWS+1>self.values_length+values_to_skip or (j==0 and i<values_to_skip) else entry_state)
                if e['state'] !='disabled':
                    self.values_entry.append(e)
                if entry_state == 'normal':
                    e.bind('<Return>', self.__update_values_write)
                e.grid(column=j*2+1, row=i+1)
    






if __name__ == '__main__':
    WINDOWS = True
    SKIP_CONNECTION = False
    SKIP_TO_TABLE = False
    myApp = App()







        