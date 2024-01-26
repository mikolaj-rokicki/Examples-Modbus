from CM4_MBUS_LIB import *

master = RS485_RTU_Master(1)
devices = [1, 2]
for device in devices:
    print(master.read_multiple_holding_registers(1, device, 1))