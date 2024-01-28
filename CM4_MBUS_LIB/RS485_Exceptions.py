import logging

class Modbus_Exception(Exception):
    def __init__(self, value=None):
        self.value = value

class Initialization_Exception(Modbus_Exception):
    def __init__(self, value=None):
        super().__init__(value)

class Transmission_Exception(Modbus_Exception):
    def __init__(self, value=None):
        super().__init__(value)

class No_Connection_Exception(Transmission_Exception):
    def __init__(self, slave=None):
        super().__init__(f'No connection from slave {slave}')
        logging.log(logging.WARNING, self.value)

class Connection_Interrupted_Exception(Transmission_Exception):
    def __init__(self, slave=None, value=None):
        super().__init__(f'Slave {slave}: {value}')
        logging.log(logging.WARNING, self.value)

class Slave_Exception(Modbus_Exception):
    def __init__(self, value=None):
        super().__init__(value)

class Illegal_Function(Slave_Exception):
    def __init__(self, value=None):
        super().__init__(value)

class Illegal_Data_Address(Slave_Exception):
    def __init__(self, value=None):
        super().__init__(value)

class Illegal_Data_Value(Slave_Exception):
    def __init__(self, value=None):
        super().__init__(value)

class Slave_Device_Failure(Slave_Exception):
    def __init__(self, value=None):
        super().__init__(value)
        
class Acknowledge(Slave_Exception):
    def __init__(self, value=None):
        super().__init__(value)

class Slave_Device_Busy(Slave_Exception):
    def __init__(self, value=None):
        super().__init__(value)

class Negative_Acknowledge(Slave_Exception):
    def __init__(self, value=None):
        super().__init__(value)
        
class Memory_Parity_Error(Slave_Exception):
    def __init__(self, value=None):
        super().__init__(value)
