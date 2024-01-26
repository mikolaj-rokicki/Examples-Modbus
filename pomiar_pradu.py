from CM4_MBUS_LIB import *
import serial
from datetime import datetime
# sprawdzenie czy parametry urządzenia są domyślne
params, master = Scanner.identify_network_params(1, list(range(1, 248)), [9600, 1200, 2400, 4800], [serial.PARITY_EVEN], [1], [8])

# monitorowanie mocy
address = 1
active_power = []
reactive_power = []
for i in range(0, 1000): # 100 sekund co 0.1s
    prev_time = datetime.now()
    try: 
        active_power.append(master.read_multiple_holding_registers(address, int(0x142), 2))
    except:
        active_power.append(None)
    try: 
        reactive_power.append(master.read_multiple_holding_registers(address, int(0x148), 2))
    except:
        reactive_power.append(None)