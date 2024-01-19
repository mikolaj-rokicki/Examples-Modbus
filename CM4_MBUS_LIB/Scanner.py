import logging
import serial
from .RS485_RTU_Master import RS485_RTU_Master
from .RS485_Exceptions import *
import sys
import math
from typing import Literal



class Scanner:

    DEVICE_ADDRESSES = [1]
    REGISTER_ADDRESSES = [list(range(10, 150))]

    def identify_network_params(com_port: None | int, addresses: list[int] = None, baudrates: list = None, parities: list = None, stopbits: list = None, bytesizes: list = None) -> tuple[dict, RS485_RTU_Master]:

        if not addresses:
            addresses = range(1, 248)
        if not baudrates:
            baudrates = [1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 76800, 115200]
        if not parities:
            parities = [serial.PARITY_NONE, serial.PARITY_EVEN, serial.PARITY_ODD, serial.PARITY_MARK, serial.PARITY_SPACE]
        if not stopbits:
            stopbits = [serial.STOPBITS_ONE, serial.STOPBITS_ONE_POINT_FIVE, serial.STOPBITS_TWO]
        if not bytesizes:
            bytesizes = [serial.FIVEBITS, serial.SIXBITS, serial.SEVENBITS, serial.EIGHTBITS]



        for address in addresses:
            for baudrate in baudrates:
                for parity in parities:
                    for stopbit in stopbits:
                        for bytesize in bytesizes:
                            try:
                                if sys.platform !='win32':
                                    temp_master = RS485_RTU_Master(
                                        com_port, 
                                        baudrate=baudrate, 
                                        parity=parity, 
                                        stopbits = stopbit, 
                                        bytesize=bytesize
                                    )
                                    temp_master.read_coils(address, 1, 1)
                                else:
                                    if address not in Scanner.DEVICE_ADDRESSES or baudrate != 19200 or parity is not serial.PARITY_NONE or stopbit is not serial.STOPBITS_ONE or bytesize is not serial.EIGHTBITS:
                                        raise No_Connection_Exception(address)
                                    else:
                                        temp_master = RS485_RTU_Master(
                                            com_port, 
                                            baudrate=baudrate, 
                                            parity=parity, 
                                            stopbits = stopbit, 
                                            bytesize=bytesize
                                        )
                                        raise Slave_Exception
                                    
                                params = {
                                    'baudrate': baudrate,
                                    'parity': parity,
                                    'stopbit': stopbit,
                                    'bytesize': bytesize,
                                    'first_address': address
                                }
                                logging.debug(f'network diagnosis completed, params: {params}')
                                return params, temp_master

                            except Modbus_Exception as e:
                                ret, params = Scanner.handle_exception(e, address, baudrate, parity, stopbit, bytesize)
                                if ret:
                                    return params, temp_master

        raise Exception('no devices found')
    
    def handle_exception(e, address, baudrate, parity, stopbit, bytesize) -> tuple[bool, dict]:
        params = {
            'baudrate': baudrate,
            'parity': parity,
            'stopbit': stopbit,
            'bytesize': bytesize,
            'first_address': address
        }
        if isinstance(e, Initialization_Exception):
            logging.exception(f'found Initialization exception "{str(e.value)}", {params}')
            raise e
        if isinstance(e, No_Connection_Exception):
            logging.debug(f'no connection during network diagnostics, {params}')
            return (False, params)
        if isinstance(e, Slave_Exception):
            logging.info(f'received slave exception "{str(e)}", {params}')
            return (True, params)
        else:
            raise e
    
    def list_devices_in_network(master: RS485_RTU_Master, addresses = None) -> list[int]:
        if not addresses:
            addresses = range(1, 247)
        logging.info(f'starting devices listing')
        correct_addreses = []
        for address in addresses:
            try:
                if sys.platform == 'win32':
                    if address not in Scanner.DEVICE_ADDRESSES:
                        raise No_Connection_Exception
                    else:
                        raise Slave_Exception
                else:
                    master.read_coils(address, 1, 1)
                correct_addreses.append(address)

            except No_Connection_Exception:
                logging.debug(f'no connection during device identification, address: {address}')
                continue
            except Slave_Exception as e:
                logging.info(f'Slave exception {e} found on adress {address}')          
                correct_addreses.append(address)

        return correct_addreses

    def list_supportable_fc_in_device(master: RS485_RTU_Master, device_address, function_codes = None) -> list:
        if not function_codes:
            function_codes = [b'\x01', b'\x02',b'\x03', b'\x04', b'\x05', b'\x06', b'\x0F', b'\x10']
        supported_fc = []

        if sys.platform == 'win32':
            if b'\x03' in function_codes:
                supported_fc.append(b'\x03')
            if b'\x10' in function_codes:
                supported_fc.append(b'\x10')
            return supported_fc
        
        for fc in function_codes:
            try:
                if fc == b'\x01':
                    master.read_coils(device_address, 0, 1)
                elif fc == b'\x02':
                    master.read_discrete_inputs(device_address, 0, 1)
                elif fc == b'\x03':
                    master.read_multiple_holding_registers(device_address, 0, 1)
                elif fc == b'\x04':
                    master.read_input_registers(device_address, 0, 1)
                elif fc == b'\x05':
                    master.write_single_coil(device_address, 0, True)
                elif fc == b'\x06':
                    master.write_single_holding_register(device_address, 0, 0)
                elif fc == b'\x0F':
                    master.write_multiple_coils(device_address, 0, [True])
                elif fc == b'\x10':
                    master.write_multiple_holding_registers(device_address, 0, [0])
                else:
                    raise Exception('fc not supported in this library')
                supported_fc.append(fc)
            except Slave_Device_Failure as e:
                logging.exception(f'exception {e} during fc diagnosis')
                raise e
            except Illegal_Function as e:
                logging.debug(f'illegal function {e} during fc diagnosis')
                continue
            except Slave_Exception as e:
                logging.debug(f'other slave exception thrown during fc diagnosis{e}')
                supported_fc.append(fc)
        return supported_fc
    
    def list_supportable_addresses(master: RS485_RTU_Master, device_address, addresses: tuple[int, int], type: Literal['DI', 'Coils', 'IR', 'HR']) -> list[tuple]:
        functions_dict = {
            'DI': master.read_discrete_inputs,
            'Coils': master.read_coils,
            'IR': master.read_input_registers,
            'HR': master.read_multiple_holding_registers
        }
        max_read = 2000 if type == 'Coils' or type == 'DI' else 125
        reading_function = functions_dict[type]
        if sys.platform == 'win32':
            reading_function = Scanner.__temp_function
        addresses_no = addresses[1]-addresses[0]+1
        groups_no = math.ceil(addresses_no/max_read)
        last_tuple_length = max_read if addresses_no % max_read == 0 else addresses_no % max_read
        results = [Scanner.__avialable_addresses(device_address, reading_function, (addresses[0]+i*max_read, addresses[0]+(i+1)*max_read-1)) for i in range(0, groups_no-1)]
        results.append(Scanner.__avialable_addresses(device_address, reading_function, (addresses[0]+(groups_no-1)*max_read, addresses[1])))
        results = [item for sublist in results for item in sublist]
        final_result = []

        if results:        
            current_tuple = results[0]
            for next_tuple in results[1:]:
                if current_tuple[1] + 1 == next_tuple[0]:
                    current_tuple = (current_tuple[0], next_tuple[1])
                else:
                    final_result.append(current_tuple)
                    current_tuple = next_tuple

            final_result.append(current_tuple)
        return final_result

    def list_supportable_addresses_toghether(master: RS485_RTU_Master, device_address, addresses: tuple[int, int], type: Literal['DI', 'Coils', 'IR', 'HR']) -> tuple[int, int]:
        functions_dict = {
            'DI': master.read_discrete_inputs,
            'Coils': master.read_coils,
            'IR': master.read_input_registers,
            'HR': master.read_multiple_holding_registers
        }
        reading_function = functions_dict[type]
        if sys.platform == 'win32':
            reading_function = Scanner.__temp_function
        return (addresses[0], Scanner.__avialable_addresses_toghether(device_address, reading_function, addresses, math.ceil((addresses[0]+addresses[1])/2)))

    def __temp_function(device_address, start, length):
        if device_address not in Scanner.DEVICE_ADDRESSES:
            raise Modbus_Exception
        for i in range(start, start+length):
            if i not in [address for device in Scanner.REGISTER_ADDRESSES for address in device]:
                raise Illegal_Data_Address
             
        
    def __avialable_addresses(device_address, reading_function, addresses: tuple[int, int]) -> tuple[int, int]:
        length = addresses[1]-addresses[0]+1
        try:
            reading_function(device_address, addresses[0], length)
            return [addresses]
        except Illegal_Data_Address:
            pass
        if length == 1:
            return []
        else:
            small = Scanner.__avialable_addresses(device_address, reading_function, (addresses[0], addresses[0]+math.floor(length/2)-1))
            big = Scanner.__avialable_addresses(device_address, reading_function, (addresses[0]+math.floor(length/2), addresses[1]))
            if small and big:
                if small[-1][1]+1 == big[0][0]:
                    return small[:-1]+[(small[-1][0], big[0][1])]+big[1:0]
            return small+big

    def __avialable_addresses_toghether(device_address, reading_function, min_max: tuple[int, int], own_address) -> int:
        try:
            reading_function(device_address, own_address, 1)
            readable = True
        except Illegal_Data_Address:
            readable = False
        if readable:
            if min_max[1] == own_address:
                return own_address
            else:
                return Scanner.__avialable_addresses_toghether(device_address, reading_function, (own_address, min_max[1]), math.ceil((own_address+min_max[1])/2))
        else:
            if min_max[0] == own_address:
                return None
            elif min_max[0] == own_address-1:
                return own_address-1
            else:
                return Scanner.__avialable_addresses_toghether(device_address, reading_function, (min_max[0], own_address-1), math.ceil((min_max[0]+own_address-1)/2))

                                                            
            
    

