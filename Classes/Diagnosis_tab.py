from CM4_MBUS_LIB import *
from tkinter import *
import customtkinter as ctk
import serial
import logging


class Diagnosis_tab:
    def __init__ (self, root, app):
        from .App import App
        self.app = app
        
        self.window = Toplevel(root)
        self.window.title('Create Connection')
        self.window.geometry('800x400')
        self.window.grab_set()

        devices_identification_frame = LabelFrame(self.window, text='Devices Identification')
        devices_identification_frame.grid(row=0, column=0)
        
        devices_identification_settings_frame = LabelFrame(devices_identification_frame, text='Devices Identification Settings')
        devices_identification_settings_frame.grid(column=0,row=0)
        devices_identification_results_frame = LabelFrame(devices_identification_frame, text='Devices Identification Results')
        devices_identification_results_frame.grid(column=1, row=0)


        self.com_port_combo = self.__create_param('COM Port', App.COMS, devices_identification_settings_frame)
        self.bool_identify_devices = BooleanVar(value=False)
        devices_checbox = Checkbutton(devices_identification_settings_frame,text='identify devices', variable=self.bool_identify_devices)
        devices_checbox.pack()
        di_start_button = Button(devices_identification_settings_frame, text='start', command= self.__start_network_identification)
        di_start_button.pack()

        self.params_label = Label(devices_identification_results_frame, text='params:')
        self.params_label.pack()
        self.devices_label = Label(devices_identification_results_frame, text='devices:')
        self.devices_label.pack()


    def __create_param(self, desc, values, master_window) -> ctk.CTkComboBox :
        frame = Frame(master_window)
        frame.pack()
        label = ctk.CTkLabel(frame, text=desc)
        label.pack()
        combo = ctk.CTkComboBox(frame, values=values)
        combo.pack()
        return combo

    def __start_network_identification(self):
        from .App import App
        self.devices_list = []
        com_port = App.COMS_DICT[self.com_port_combo.get()]
        addresses = range(1, 248)
        baudrates = [App.BAUDRATE_DICT[bdr] for bdr in App.BAUDRATES]
        parities = [App.PARITY_DICT[par] for par in App.PARITIES]
        stopbits = [App.STOPBITS_DICT[stb] for stb in App.STOPBITS]
        bytesizes = [App.BYTESIZE_DICT[bs] for bs in App.BYTESIZES]
        self.master, self.params = self.identify_network(com_port, addresses, baudrates, parities, stopbits, bytesizes)
        logging.info(f'network identified with parameters {self.params}')
        first_adress = self.params['address']
        if self.bool_identify_devices.get() :
            self.devices_list = self.identify_devices(range(first_adress, 248))
            logging.info(f'network identified with addresses {self.devices_list}')
        self.__update_device_identification_results()

    def identify_network(self, com_port: None | int, addresses, baudrates, parities, stopbits, bytesizes) -> tuple[RS485_RTU_Master, list]:

        for address in addresses:
            for baudrate in baudrates:
                for parity in parities:
                    for stopbit in stopbits:
                        for bytesize in bytesizes:
                            try:
                                if not self.app.WINDOWS:
                                    temp_master = RS485_RTU_Master(
                                        com_port, 
                                        baudrate=baudrate, 
                                        parity=parity, 
                                        stopbits = stopbit, 
                                        bytesize=bytesize
                                    )
                                    temp_master.read_coils(address, 1, 1)
                                else:
                                    if address not in self.app.DEVICE_ADDRESSES or baudrate != 19200 or parity is not serial.PARITY_NONE or stopbit is not serial.STOPBITS_ONE or bytesize is not serial.EIGHTBITS:
                                        raise RS485_RTU_Master.No_Connection_Exception(address)
                                    else:
                                        temp_master = RS485_RTU_Master(
                                            com_port, 
                                            baudrate=baudrate, 
                                            parity=parity, 
                                            stopbits = stopbit, 
                                            bytesize=bytesize
                                        )
                                        raise RS485_RTU_Master.Modbus_Exception
                                    
                                logging.debug(f'network diagnosis completed, params: {com_port, address, parity, stopbit, bytesize} (com, adr, par, stb, bytsize)')
                                return temp_master, {
                                    'address': address,
                                    'baudrate': baudrate,
                                    'parity': parity,
                                    'stopbit': stopbit,
                                    'bytesize': bytesize
                                }
                            except RS485_RTU_Master.Initialization_Exception as e:
                                logging.exception(f'found other exception "{str(e)}", params: {com_port, address, parity, stopbit, bytesize} (com, adr, par, stb, bytsize)')
                                raise e
                            except RS485_RTU_Master.No_Connection_Exception:
                                logging.debug(f'no connection during diagnostics, params: {com_port, address, parity, stopbit, bytesize} (com, adr, par, stb, bytsize)')
                                continue
                            except RS485_RTU_Master.Modbus_Exception as e:
                                logging.info(f'received modbus_exception "{str(e)}", params: {com_port, address, parity, stopbit, bytesize} (com, adr, par, stb, bytsize)')
                                return temp_master, {
                                    'address': address,
                                    'baudrate': baudrate,
                                    'parity': parity,
                                    'stopbit': stopbit,
                                    'bytesize': bytesize
                                }

        raise Exception('no devices found')


    def identify_devices(self, addresses) -> list[int]:
        correct_addreses = []
        for address in addresses:
            try:
                if self.app.WINDOWS:
                    if address not in self.app.DEVICE_ADDRESSES:
                        raise RS485_RTU_Master.No_Connection_Exception
                    else:
                        raise RS485_RTU_Master.Modbus_Exception
                else:
                    self.master.read_coils(address, 1, 1)
                correct_addreses.append(address)
            except RS485_RTU_Master.No_Connection_Exception:
                logging.debug(f'no connection during device identification, address: {address}')
                continue
            except RS485_RTU_Master.Modbus_Exception as e:
                logging.info(f'modbus exception {e} found on adress {address}')
                correct_addreses.append(address)
        return correct_addreses
    
    def __update_device_identification_results(self):
        self.params_label.config(text=f'params: {self.params}')
        self.devices_label.config(text=f'devices: {self.devices_list}')
