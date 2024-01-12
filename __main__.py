from tkinter import *
import customtkinter
from tkinter import ttk
import math
from typing import Literal
from CM4_MBUS_LIB import RS485_RTU_Master
import serial

class App:
    REGISTER_VALUES = [5689, 2354, 15734, 62453, 16582, 9453, 109, 652, 2134, 10, 11, 12, 13, 14]
    def __init__(self):
        self.root = Tk()
        self.root.title('Modbus Master')
        self.root.geometry('800x480')
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
            self.root.after(15, lambda: self.__create_settings([True, True]))
            self.root.after(20, lambda: self.__create_table(0, 123))
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
        conn.grab_release()
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
            '01: Read Coils': [True, False], # length, writtable
            '02: Read Discrete Inputs': [True, False],
            '03: Read Multiple Holding Registers': [True, False],
            '04: Read Input Registers': [True, False],
            '05: Write Single Coil': [False, True],
            '06: Write Single Holding Register': [False, True],
            '15: Write Multiple Coils': [True, True],
            '16: Write Multiple Holding Registers': [True, True]
        }
        function_code_combo = ttk.Combobox(function_code_frame, values=FUNCTION_CODES)
        function_code_combo.set(FUNCTION_CODES[0])
        function_code_combo.pack()
        confirm_button = Button(function_code_frame, text='Ok', command= lambda: self.__create_settings(FUNCTION_CODES_DICT[function_code_combo.get()]))
        confirm_button.pack()
        self.connection_menu.entryconfig('Delete Connection', state=NORMAL)

    def __create_settings(self, params):
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
        confirm_button = Button(device_settings_frame_bottom, text='OK', command=lambda: self.__update_device(device_ID_box.get(), adress_box.get(), length_box.get()))
        confirm_button.pack(side=LEFT)

        self.display_settings_frame = LabelFrame(self.settings_frame, text='Display Settings')
        self.display_settings_frame.pack(side=LEFT)
        DISPLAY_TYPES = ['ASCII', 'Integer','Hexadecimal', 'Binary']

        self.display_type: Literal['ASCII', 'Integer','Hexadecimal', 'Binary'] = 'Integer'
        display_type_label = Label(self.display_settings_frame, text='Display Type')
        display_type_label.pack()
        self.display_type_combo = ttk.Combobox(self.display_settings_frame, values = DISPLAY_TYPES)
        self.display_type_combo.set(self.display_type)
        self.display_type_combo.pack()
        confirm_button = Button(self.display_settings_frame, text='OK', command=lambda: self.__update_display_type())
        confirm_button.pack()
    
    def __delete_settings(self):
        self.settings_frame.destroy()
        self.connection_menu.entryconfig('Create Connection', state=NORMAL)
        self.__delete_table_canvas()
        self.connection_menu.entryconfig('Delete Connection', state=DISABLED)

    def __update_display_type(self):
        self.display_type = self.display_type_combo.get()
        old_info = self.info_label.cget('text')
        self.info_label.config(text='display type updated')
        self.root.after(500, lambda: self.info_label.config(text=old_info))

    def __update_registers(self):
        # TODO: pool data
        for i, value in enumerate(self.values, start=0):
            if i<self.values_length:
                value.configure(state=NORMAL)
                value.delete(0, END)
                if self.display_type == 'Integer':
                    value.insert(0, f'{App.REGISTER_VALUES[i]}')
                elif self.display_type == 'Binary':
                    value.insert(0, f'{bin(App.REGISTER_VALUES[i])[2:]}')
                elif self.display_type == 'Hexadecimal':
                    value.insert(0, f'{hex(App.REGISTER_VALUES[i])[2:]}')
                elif self.display_type == 'ASCII':
                    value.insert(0, f'{chr(App.REGISTER_VALUES[i])}')
                value.configure(state='readonly')
        self.root.after(1000, lambda: self.__update_registers())

    def __update_device(self, device_ID: str, adress: str, length: str):
        try:
            device_ID = int(device_ID)
            adress = int(adress)
            length = int(length)
            self.__create_table(adress, length)
        except Exception as e:
            self.info_label.config(text=str(e))

    def __delete_table_canvas(self):
        if hasattr(self, 'canvas'):
            self.canvas.destroy()

    def __update_canvas_borders(self):
        self.canvas.config(scrollregion=(0, 0, self.table.winfo_reqwidth()+20, self.table.winfo_reqheight()+20))

    def __create_table(self, adress, length):
        self.__delete_table_canvas()
        self.canvas = Canvas(self.root, scrollregion=(0, 0, 10000, 1000), bg='yellow')
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        canvas_scroll_bar = Scrollbar(self.canvas, orient=HORIZONTAL, command=self.canvas.xview) 
        canvas_scroll_bar.pack(side=BOTTOM, fill=X)
        self.canvas.config(xscrollcommand=canvas_scroll_bar.set)
        self.table = Frame(self.canvas)
        self.canvas.create_window(10, 10, window=self.table, anchor='nw')
        self.root.after(60, lambda: self.__update_canvas_borders())
        self.values_length = length
        ROWS = 10
        columns = 2*math.ceil(self.values_length/ROWS)
        top_left_corner = Label(self.table, width=20, background='lightgray', borderwidth=1, relief='solid')
        top_left_corner.grid(column=0, row=0)
        # left column
        left_column = [Label(self.table, text=i, width=20, background='lightgray', borderwidth=1, relief='solid') for i in range(0,10)]
        for i in range(0, ROWS):
            left_column[i].grid(column=0, row=i+1)
        # top row
        top_row = [Label(self.table, text= 'alias' if i%2==0 else f'{int(((i-1)/2)*ROWS)}', width=20, background='lightgray', borderwidth=1, relief='solid') for i in range(0, columns)]
        for j in range(0, columns):
            top_row[j].grid(column=j+1, row=0)
        # aliases
        for i in range(0, ROWS):
            for j in range(0, int(columns/2)):
                e = Entry(self.table, width=20, disabledbackground='lightgray', state=DISABLED if i+j*ROWS+1>self.values_length else NORMAL)
                e.grid(column=j*2+1, row=i+1)
        # values
        self.values: list[Entry] = []
        for j in range(0, int(columns/2)):
            for i in range(0, ROWS):
                e = Entry(self.table, width=20, disabledbackground='lightgray', state='disabled' if i+j*ROWS+1>self.values_length else 'readonly')
                self.values.append(e)
                e.grid(column=j*2+2, row=i+1)
    






if __name__ == '__main__':
    WINDOWS = True
    SKIP_CONNECTION = True
    SKIP_TO_TABLE = True
    myApp = App()







        