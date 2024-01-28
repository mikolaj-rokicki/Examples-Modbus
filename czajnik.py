from CM4_MBUS_LIB import *
from datetime import datetime
import matplotlib.pyplot as plt

master = RS485_RTU_Master(1, baudrate = 9600, parity = 'E', stopbits = 1)
#print(master.read_multiple_holding_registers(1, int(0x110), 1))
#params, master = Scanner.identify_network_params(1, list(range(1, 10)), [9600, 1200, 2400, 4800], ['E'], [1], [8])
#print(params)
active_power = []
for i in range(0, 1000):
    start_time = datetime.now()
    read = master.read_multiple_holding_registers(1, int(0x140), 2)
    active_power.append(read[0]*int(0x10000)+read[1])
    while ((datetime.now()-start_time).total_seconds()) < 0.1 :
        sleep(0.01)
time = [i/10 for i in range(0, 1000)]
plt.plot(time, active_power)
plt.show()

    
