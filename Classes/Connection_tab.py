from CM4_MBUS_LIB import *
from tkinter import *
import customtkinter as ctk
from typing import Literal


class Connection_tab:
    def __init__ (self, root, app, action_type: Literal['new', 'change'] = 'new'):
        from .App import App
        self.app = app
        
        self.window = Toplevel(root)
        self.window.title('Create Connection')
        self.window.geometry('400x400')
        self.window.grab_set()

        com_port_combo = self.__create_param('COM Port', App.COMS, self.window)
        baudrate_combo = self.__create_param('Baudrate', App.BAUDRATES, self.window)
        parity_bits_combo = self.__create_param('Parity Bits', App.PARITIES, self.window)
        stop_bits_combo = self.__create_param('Stop Bits', App.STOPBITS, self.window)
        byte_size_combo = self.__create_param('Bytesize', App.BYTESIZES, self.window)

        self.info_frame = ctk.CTkFrame(self.window, width=400)
        self.info_frame.pack(side = BOTTOM)
        self.conn_info_label = Label(self.info_frame, text='ready', anchor=E, padx=10)
        self.conn_info_label.pack(side = LEFT, expand=1, fill=X)
        self.window.after(30, lambda: self.conn_info_label.config(width = self.window.winfo_width()))
        
        if action_type == 'new':
            create_button = ctk.CTkButton(
                self.window, 
                text='Create Connection', 
                command= lambda: self.__create_connection(
                                                            com_port_combo.get(), 
                                                            baudrate_combo.get(), 
                                                            parity_bits_combo.get(), 
                                                            stop_bits_combo.get(), 
                                                            byte_size_combo.get()
                )
            )
        else:
            create_button = ctk.CTkButton(
                self.window, 
                text='Change Connection', 
                command= lambda: self.__edit_connection(
                                                            com_port_combo.get(), 
                                                            baudrate_combo.get(), 
                                                            parity_bits_combo.get(), 
                                                            stop_bits_combo.get(), 
                                                            byte_size_combo.get()
                )
            )
        create_button.pack(pady = 10)


    def __create_param(self, desc, values, master_window) -> ctk.CTkComboBox :
        frame = Frame(master_window)
        frame.pack()
        label = ctk.CTkLabel(frame, text=desc)
        label.pack()
        combo = ctk.CTkComboBox(frame, values=values)
        combo.pack()
        return combo
    
    def __create_connection(self, port_no, baudrate, parity, stopbits, bytesize):
        from .App import App
        try:
            master = RS485_RTU_Master(App.COMS_DICT[port_no], 
                                                        baudrate=App.BAUDRATE_DICT[baudrate], 
                                                        parity=App.PARITY_DICT[parity], 
                                                        stopbits=App.STOPBITS_DICT[stopbits], 
                                                        bytesize=App.BYTESIZE_DICT[bytesize]
                                                        )
        except Exception as e:
            self.conn_info_label.configure(text = str(e))
            logging.exception(f'{e}')
            return
        
        params = [port_no, baudrate, parity, stopbits, bytesize]
        self.window.grab_release()
        self.app.assign_master(master, params, self)
    
    def __edit_connection(self, port_no, baudrate, parity, stopbits, bytesize):
        from .App import App
        RS485_RTU_Master.convigure_overlap_checking(False)
        try:
            master = RS485_RTU_Master(App.COMS_DICT[port_no], 
                                                        baudrate=App.BAUDRATE_DICT[baudrate], 
                                                        parity=App.PARITY_DICT[parity], 
                                                        stopbits=App.STOPBITS_DICT[stopbits], 
                                                        bytesize=App.BYTESIZE_DICT[bytesize]
                                                        )
            RS485_RTU_Master.convigure_overlap_checking(True)
        except Exception as e:
            self.conn_info_label.configure(text = str(e))
            return
        
        params = [port_no, baudrate, parity, stopbits, bytesize]
        self.window.grab_release()
        self.app.edit_master(master, params, self)

