from CM4_MBUS_LIB import *
from tkinter import *
import serial
import logging
import pickle
from tkinter import filedialog
from .Connection_tab import Connection_tab
from .Connection import Connection
from .Diagnosis_tab import Diagnosis_tab
from .Device import Device
from typing import Literal



class App:
        
    COMS_DICT = {
        'COM0': 0,
        'COM1': 1,
        'COM2': 2,
        'COM3': 3,
        'NONE': None
    }        
    BAUDRATE_DICT = {
        '1200': 1200, 
        '2400': 2400, 
        '4800': 4800, 
        '9600': 9600, 
        '14400': 14400, 
        '19200': 19200, 
        '28800': 28800, 
        '38400': 38400, 
        '57600': 57600, 
        '76800': 76800, 
        '115200': 115200
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

    COMS = ['COM0', 'COM1', 'COM2', 'COM3', 'NONE']
    BAUDRATES = ['1200', '2400', '4800', '9600', '14400', '19200', '28800', '38400', '57600', '76800', '115200']
    PARITIES = ['NONE']
    STOPBITS = ['ONE', 'TWO']
    BYTESIZES = ['8 bits', '5 bits']

    def __init__(self, WINDOWS = False, SKIP_CONNECTION = False, SKIP_TO_TABLE = False, DEVICE_ADDRESSES = [], REGISTER_ADDRESSES = []):
        
        self.WINDOWS = WINDOWS
        self.DEVICE_ADDRESSES = DEVICE_ADDRESSES
        self.REGISTER_ADDRESSES = REGISTER_ADDRESSES
        logging.log(logging.INFO, 'app created')

        self.__create_root_window()        
        self.__create_menu()

        self.info_label = Label(self.root, text='Establish Connection First', anchor=E, padx=10)
        self.info_label.pack(side=BOTTOM)
        self.root.after(1, lambda: self.info_label.config(width=self.root.winfo_width()))



        self.root.after(100, lambda: self.__skip(SKIP_CONNECTION, SKIP_TO_TABLE))

        self.root.mainloop()

    def __create_root_window(self):
        self.root = Tk()
        self.root.title('New File')
        self.root.geometry('900x680')

    def __create_menu(self):
        self._main_menu = Menu(self.root)
        self.root.config(menu=self._main_menu)

        self.file_menu = Menu(self._main_menu, tearoff=False)
        self._main_menu.add_cascade(label='File', menu=self.file_menu)
        self.file_menu.add_command(label='New File', command = self.__new_file)
        self.file_menu.add_command(label='Save', command = lambda: self.__save(), state='disabled')
        self.file_menu.add_command(label='Save As', command = lambda: self.__save_as(), state='disabled')
        self.file_menu.add_command(label= 'Load', command = self.__load)
        
        self.connection_menu = Menu(self._main_menu, tearoff=False)
        self._main_menu.add_cascade(label='Connections', menu=self.connection_menu)
        self.connection_menu.add_command(label='Create Connection', command = self.__create_connection_tab)
        self.connection_menu.add_command(label='Edit Connection', command = lambda: self.__create_connection_tab('change'), state=DISABLED)
        self.connection_menu.add_command(label= 'Delete Connection', command = self.__delete_connection, state=DISABLED)

        self.network_menu = Menu(self._main_menu, tearoff=False)
        self._main_menu.add_cascade(label='Network', menu=self.network_menu)
        self.network_menu.add_command(label='Diagnosis', command = self.__create_diagnosis_tab)

        self.devices_menu = Menu(self._main_menu, tearoff=False)
        self._main_menu.add_cascade(label='Devices', menu=self.devices_menu)
        self.devices_menu.add_command(label='Delete Devices', command = self.__clear_devices, state=DISABLED)

    def __skip(self, SKIP_CONNECTION, SKIP_TO_TABLE):
        # TODO: delete lambdas
        if SKIP_CONNECTION:
            self.assign_master(RS485_RTU_Master())
        if SKIP_TO_TABLE:
            if not SKIP_CONNECTION:
                self.__skip(True, True)
            self.connection.add_new_device(1)
            device: Device = self.connection.devices[0]
            device.add_new_task(1, 123, b'\x10')

        pass

    def __create_connection_tab(self, action_type: Literal['new', 'change'] = 'new'):
        logging.log(logging.DEBUG, 'connection tab created')
        Connection_tab(self.root, self, action_type)

    def __create_diagnosis_tab(self):
        logging.log(logging.DEBUG, 'diagnosis tab created')
        Diagnosis_tab(self.root, self)

    def assign_master(self, master: RS485_RTU_Master, params = None, conn = None):
        # master assigned
        self.master = master
        if conn is not None:
            conn.window.destroy()

        self.connection_frame = Frame(self.root, background='yellow')
        self.connection_frame.pack(fill='both', expand=1)
        self.connection = Connection(self, self.connection_frame, params)
        
        self.connection_menu.entryconfig('Create Connection', state=DISABLED)
        self.connection_menu.entryconfig('Edit Connection', state=NORMAL)
        self.connection_menu.entryconfig('Delete Connection', state=NORMAL)
        self.file_menu.entryconfig('Save', state=NORMAL)
        self.file_menu.entryconfig('Save As', state=NORMAL)

    def __delete_connection(self):
        if hasattr(self, 'master'):
            self.master.destroy()
            del self.master
        if hasattr(self, 'connection'):
            self.connection.destroy()
            del self.connection
        
        self.connection_menu.entryconfig('Create Connection', state=NORMAL)
        self.connection_menu.entryconfig('Edit Connection', state=DISABLED)
        self.connection_menu.entryconfig('Delete Connection', state=DISABLED)
        self.file_menu.entryconfig('Save', state=DISABLED)
        self.file_menu.entryconfig('Save As', state=DISABLED)
    
    def edit_master(self, master: RS485_RTU_Master, params, conn = None):
        # master assigned
        self.master.destroy()
        self.master = master
        if conn is not None:
            conn.window.destroy()
        self.connection.change_connection(master, params[0], params[1], params[2], params[3], params[4])

    def __clear_devices(self):
        self.connection.delete_devices()

    def __new_file(self):
        if hasattr(self, 'connection'):
            self.__delete_connection()
        self.root.title('New File')

    def __save(self, file_path = None):
        if not file_path:
            file_path = self.root.title()+'.pkl'
        save_data_connection = self.connection.params
        save_data_other = []
        for device in self.connection.devices:
            device_address = device.address
            tasks = []
            for task in device.tasks:
                tasks.append((task.function_code, task.starting_adress, task.length))
            save_data_other.append((device_address, tasks))
        save_data = (save_data_connection, save_data_other)
        
        with open(file_path, 'wb') as file:
            pickle.dump(save_data, file)

    def __save_as(self):
        file_path = filedialog.asksaveasfilename(title='Save As', filetypes=(('Save As', '*.pkl'), ), defaultextension='.pkl')
        self.__save(file_path)
        last_dot_index = file_path.rfind('.')
        if last_dot_index != -1:  # Check if dot is found
            file_name = file_path[:last_dot_index]
        else:
            file_name = file_path
        self.root.title(file_name)

    def __load(self):
        file_path = filedialog.askopenfilename(title='Open File', filetypes=(('Save Files', '*.pkl'), ('All files', '*.*')))
        
        with open(file_path, 'rb') as file:
            save_data = pickle.load(file)
        params = save_data[0]
        self.__delete_connection()
        if self.__load_connection(params):
            return
        for device in save_data[1]:
            self.__load_device(device[0], device[1])
            

    def __load_connection(self, params: dict):
        try:
            master = RS485_RTU_Master(
                App.COMS_DICT[params['port_no']], 
                baudrate=App.BAUDRATE_DICT[params['baudrate']], 
                parity=App.PARITY_DICT[params['parity']], 
                stopbits=App.STOPBITS_DICT[params['stopbits']], 
                bytesize=App.BYTESIZE_DICT[params['bytesize']]
            )
        except Exception as e:
            self.info_label.configure(text = str(e))
            return True
        self.assign_master(master, params)
        return False
    
    def __load_device(self, address, tasks):
        device = self.connection.add_new_device(address)
        for task in tasks:
            device.add_new_task(task[1], task[2], task[0])
    
    


      





