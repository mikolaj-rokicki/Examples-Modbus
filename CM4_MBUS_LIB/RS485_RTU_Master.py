import sys
if sys.platform == 'win32':
    import CM4_MBUS_LIB.RPi.GPIO as GPIO
else:
    import RPi.GPIO
import serial
from time import sleep
import logging
from typing import Union, Literal
import math
from .RS485_Exceptions import *




class RS485_RTU_Master:
    PORTS_DEFAULTS = ((None, 10), ('/dev/ttyAMA3', 27), ('/dev/ttyAMA4', 7), ('/dev/ttyAMA0', 21))
    other_clients = [[],[],[]] #ports, devs, f_c ports

    # START of Initial configuration
    def __init__(self, port_no: int | None = None, dev = None, flow_control_port: int = None, **kwargs: Literal['baudrate','parity','stopbits','bytesize']):
        if port_no is None:
            logging.log(logging.WARNING, 'RS485_RTU_Master initialisation passed!')
            baudrate = kwargs.get('baudrate', 19200)
            parity = kwargs.get('parity', serial.PARITY_NONE)
            stopbits = kwargs.get('stopbits', serial.STOPBITS_ONE)
            bytesize = kwargs.get('bytesize', serial.EIGHTBITS)
            self.params = {
            'port_no': port_no,
            'baudrate': baudrate,
            'parity': parity,
            'stopbits': stopbits,
            'bytesize': bytesize
            }
            return
        self.__overlap_checking = True
        if type(port_no) is not int:
            raise Initialization_Exception('port_no has to be an integer')
        # Assign default values
        if dev is None or flow_control_port is None:
            if len(RS485_RTU_Master.PORTS_DEFAULTS)-1 < port_no:
                raise Initialization_Exception('port_no not in range of supported defaults')
            if dev == None:
                dev = RS485_RTU_Master.PORTS_DEFAULTS[port_no][0]
                if dev == None:
                    raise Initialization_Exception('Not avialable default device name for this port')
            if flow_control_port == None:
                flow_control_port = RS485_RTU_Master.PORTS_DEFAULTS[port_no][1]
                if flow_control_port == None:
                    raise Initialization_Exception('Not avialable default flow control port for this port')
        if type(dev) is not str:
            raise Initialization_Exception('argument dev has to be string')
        if type(flow_control_port) is not int:
            raise Initialization_Exception('argument flow_control_port has to be a string')

        self.port_no = port_no
        self.dev = dev
        self.flow_control_port = flow_control_port

        if self.__overlap_checking:
            if self.__check_overlap():
                raise Initialization_Exception('Found overlaping ports/device names to turn off this exception use method configure_overlap_checking(False)')
        self.__configure_fc_port()
        self.__configure_connection(**kwargs)
        RS485_RTU_Master.other_clients[0].append(port_no)
        RS485_RTU_Master.other_clients[1].append(dev)
        RS485_RTU_Master.other_clients[2].append(flow_control_port)

        self.slaves = []

    def convigure_overlap_checking(self, value: bool):
        if type(value) is not bool:
            raise Modbus_Exception('value of argument "value" has to be an bool')
        self.__overlap_checking = value

    def __check_overlap(self):
        if self.port_no in self.other_clients[0]:
            return True
        if self.port_no in self.other_clients[2]:
            return True
        if self.dev in self.other_clients[1]:
            return True
        if self.flow_control_port in self.other_clients[0]:
            return True
        if self.flow_control_port in self.other_clients[2]:
            return True
        return False
    
    def __configure_fc_port(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.flow_control_port, GPIO.OUT)
        GPIO.output(self.flow_control_port, GPIO.HIGH)
    
    def __configure_connection(self, **kwargs):
        baudrate = kwargs.get('baudrate', 19200)
        parity = kwargs.get('parity', serial.PARITY_NONE)
        stopbits = kwargs.get('stopbits', serial.STOPBITS_ONE)
        bytesize = kwargs.get('bytesize', serial.EIGHTBITS)

        self.baudrate = baudrate
        self.params = {
            'port_no': self.port_no,
            'baudrate': baudrate,
            'parity': parity,
            'stopbits': stopbits,
            'bytesize': bytesize
        }
        self.serial_port = serial.Serial(port= self.dev,
                                         baudrate=baudrate,
                                         parity=parity,
                                         stopbits=stopbits,
                                         bytesize=bytesize)
    # END of initial configuration

    # START Transfer functions
    def __send_data(self, data):
        data += self.__calculate_CRC(data)
        for i in range(1, 6):
            try:
                received_data = b''
                GPIO.output(self.flow_control_port, GPIO.LOW)
                sending_time = self.__calculate_time(len(data))
                self.serial_port.write(data)
                sleep(sending_time)
                GPIO.output(self.flow_control_port, GPIO.HIGH)
                sleep(0.1) #TODO: Calculate sleep time
                data_left = self.serial_port.inWaiting()
                if data_left == 0:
                    raise No_Connection_Exception(data[0])
                logging.log(logging.DEBUG, f'reading {str(data_left)} bytes of return message')
                received_data += self.serial_port.read(data_left)
                logging.log(logging.INFO, f'RECEIVED DATA: {received_data}')
                success = True
            except Transmission_Exception:
                success = False
            except:
                return #TODO: add return type
            if success is True:
                break            

        return received_data[-2:-2]
        #TODO: add exceptions

    def __calculate_time(self, bytes_no):
        return (bytes_no+4)*9/self.baudrate
        #TODO: make sure its good formula
    # END of transfer functions

    def __check_if_response_is_propper(self, data, response):
        if len(response<6):
            raise Connection_Interrupted_Exception(data[0], 'Response length too short')
        if data[0]!=response[0]:
            raise Connection_Interrupted_Exception(data[0], 'Response adress doesn\'t match with desired')
        if data[1]!=response[1] and data[1]+128 != response[1]:
            raise Connection_Interrupted_Exception(data[0], 'Function codes from connection and response doesn\'t match')
        response_data = response[:-2]
        crc = response[-2:]
        expected_crc = self.__calculate_CRC(response_data)
        if crc != expected_crc:
            raise Connection_Interrupted_Exception(data[0], f'CRC doesn\'t match, received CRC: {crc}, expected CRC: {expected_crc}') 

    def add_slave(self, slave_adress: int):
        self.slaves.append(RS485_RTU_Master.Slave(slave_adress))
    
    def __calculate_CRC(self, data):
        #TODO: fast conversion
        crc = 0xFFFF
        for n in range(len(data)):
            crc ^= data[n]
            for i in range(8):
                if crc & 1:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return(crc.to_bytes(2, 'little'))

    def read_discrete_inputs(self, slave_adress: int | bytes, starting_adress: int | bytes, inputs_qty: int | bytes) -> list[bool]:
        return self.__read_discrete(slave_adress, starting_adress, inputs_qty, 'DI')
    
    def read_coils(self, slave_adress: int | bytes, starting_adress: int | bytes, inputs_qty: int | bytes) -> list[bool]:
        return self.__read_discrete(slave_adress, starting_adress, inputs_qty, 'Coils')
    
    def __read_discrete(self, slave_adress: int | bytes, starting_adress: int | bytes, inputs_qty: int | bytes, fc: Literal['DI', 'Coils']) -> list[bool]:
        slave_adress = self.__check_if_int_or_byte_and_convert_in_bounds(slave_adress, 1, 0, 247)
        starting_adress = self.__check_if_int_or_byte_and_convert_in_bounds(starting_adress, 2, 0, int(0xFFFF))
        inputs_qty = self.__check_if_int_or_byte_and_convert_in_bounds(inputs_qty, 2, 1, 2000)
        if(fc) == 'DI':
            function_code = b'\x02'
        elif(fc) == 'Coils':
            function_code = b'\x01'
        response = self.__send_data(slave_adress+function_code+starting_adress+inputs_qty)
        coils = int.from_bytes(inputs_qty)
        n = math.ceil(coils/8)
        if len(response)!=(n+1):
            raise Transmission_Exception(f'Received {len(response)} bytes of data, expected {n+1} bytes')
        return self.__convert_coil_state(response[-1:])
    
    def write_single_coil(self, slave_adress: int | bytes, output_adress: int | bytes, value: bool):
        slave_adress = self.__check_if_int_or_byte_and_convert_in_bounds(slave_adress, 1, 0, 247)
        output_adress = self.__check_if_int_or_byte_and_convert_in_bounds(output_adress, 2, 0, int(0xFFFF))
        if bool(value) is True:
            value = b'\xFF\x00'
        else:
            value = b'\x00\x00'
        function_code = b'\x05'
        self.__send_data(slave_adress+function_code+output_adress+value)

    def write_multiple_coils(self, slave_adress: int | bytes, starting_adress: int | bytes, values: list[bool]):
        slave_adress = self.__check_if_int_or_byte_and_convert_in_bounds(slave_adress, 1, 0, 247)
        starting_adress = self.__check_if_int_or_byte_and_convert_in_bounds(starting_adress, 2, 0, int(0xFFFF))
        if (len(values)>int(0x07B0)) or (len(values)<1) :
            raise Modbus_Exception(f"length of values cannot be {len(values)}, it has to be between 1 and {int(0x07B0)}")
        function_code = b'\x0F'
        qty_of_inputs = len(values).to_bytes(2)
        byte_count = math.ceil(qty_of_inputs/8)
        bytes_array = [values[8*i:8*i+8] for i in range(0, byte_count)]
        values = bytearray()
        for byte in bytes_array:
            int_val = 0
            for i, b in enumerate(byte):
                int_val = int_val | b << i
            values += int_val.to_bytes(1)
        self.__send_data(slave_adress+function_code+starting_adress+qty_of_inputs+byte_count.to_bytes(1)+values)
        
    def __convert_coil_state(data: bytearray, coil_qty: int) -> list[bool]:
        bool_list = [bool((1 << i) & byte) for byte in data for i in range(0,8)]
        return bool_list[:coil_qty]

    def __check_if_int_or_byte_and_convert_in_bounds(self, value, bytes_qty = None, lower_bound: int = 0, upper_bound: int | float = float('inf'), byteorder='big') -> bytes:
        if type(value) is int:
            if(value<lower_bound or value>upper_bound):
                raise Modbus_Exception(f'value {value} is outside of bounds, it has to be between {lower_bound} and {upper_bound}')
            return value.to_bytes(bytes_qty)
        elif type(value) is bytes:
            if bytes_qty is not None:
                if(len(value) != bytes_qty):
                    raise Modbus_Exception(f'length of value {value} is {len(value)}, it has to be {bytes_qty} bytes')
            if (int.from_bytes(value, byteorder)<lower_bound or int.from_bytes(value, byteorder>upper_bound)):
                raise Modbus_Exception(f'value {int.from_bytes(value, byteorder)} is outside of bounds, it has to be between {lower_bound} and {upper_bound}')
            return value
        else:
            raise Modbus_Exception(f'type {type(value)} is supposed to be int or bytes') 

    def read_input_registers(self, slave_adress: int | bytes, starting_adress: int | bytes, input_qty: int | bytes) -> list[int]:
        return self.__read_registers(slave_adress, starting_adress, input_qty, 'Input')

    def read_multiple_holding_registers(self, slave_adress: int | bytes, starting_adress: int | bytes, registers_qty: int | bytes) -> list[int]:
        return self.__read_registers(slave_adress, starting_adress, registers_qty, 'Holding')

    def __read_registers(self, slave_adress: int | bytes, starting_adress: int | bytes, registers_qty: int | bytes, fc: Literal['Input', 'Holding']) -> list[int]:
        slave_adress = self.__check_if_int_or_byte_and_convert_in_bounds(slave_adress, 1, 0, 247)
        starting_adress = self.__check_if_int_or_byte_and_convert_in_bounds(starting_adress, 2, 0, int(0xFFFF))
        input_qty = self.__check_if_int_or_byte_and_convert_in_bounds(input_qty, 2, 1, int(0x007D))
        if fc == 'Input':
            function_code = b'\x04'
        else:
            function_code = b'\x03'
        response = self.__send_data(slave_adress+function_code+starting_adress+input_qty)
        byte_count = response[0]
        content = byte_count[1:]
        return [content[2*i]*int(0xFF)+content[2*i+1] for i in range(0, byte_count/2)]
    
    def write_single_holding_register(self, slave_adress: Union[int, bytes], register_adress: Union[int, bytes], register_value: int | bytes):
        # slave adress
        slave_adress = self.__check_if_int_or_byte_and_convert_in_bounds(slave_adress, 1, 0, 247)
        # assign function code
        function_code = b'\x06'
        # checking if register adress is propper
        register_adress = self.__check_if_int_or_byte_and_convert_in_bounds(register_adress, 2, 0, int(0xFFFF))
        register_value = self.__check_if_int_or_byte_and_convert_in_bounds(register_value, 2, 0, int(0xFFFF))
        data = slave_adress+function_code+register_adress+register_value
        logging.log(logging.INFO, f'Prepared message to send: {data.hex()}')
        self.__send_data(data)

    def write_multiple_holding_registers(self, slave_adress: Union[int, bytes], starting_register_adress: Union[int, bytes], values: list[Union[int, bytes]]):
        slave_adress = self.__check_if_int_or_byte_and_convert_in_bounds(slave_adress, 1, 0, 247)
        function_code = b'\x10'
        starting_register_adress = self.__check_if_int_or_byte_and_convert_in_bounds(starting_register_adress, 2, 0, int(0xFFFF))
        registers_qty = len(values).to_bytes(2)
        byte_count = (len(values)*2).to_bytes(1)

        # values validation
        values_bytes = b''
        if type(values)!=list:
            raise Modbus_Exception(f'Type {type(values)} is unsupported for values, supported types is list of int and bytes!')
        if len(values) > int(0x7B):
            raise Modbus_Exception(f'length of values cannot be greater than {int(0x7B)}')
        for index, value in enumerate(values):
            try:
                value = self.__check_if_int_or_byte_and_convert_in_bounds(value, 2, 0, int(0xFFFF))
            except Modbus_Exception as ex:
                raise Modbus_Exception(f'{ex.value} for values[{index}]')
            
        data = slave_adress+function_code+starting_register_adress+registers_qty+byte_count+values_bytes
        logging.log(logging.INFO, f'Prepared message to send: {data.hex()}')
        #self.__send_data(data)
        logging.log(logging.WARNING, 'Data sending is turned off')
        #TODO: enable send data

    class Slave:
        def __init__(self, master: 'RS485_RTU_Master', adress: int):
            self.client = master
            self.adress = adress
        def write_single_holding_register(self, register_adress, register_value):
            self.client.write_single_holding_register(self.adress, register_adress, register_value)
            #TODO: dodać return

        #TODO: add remaining functions

