from CM4_MBUS_LIB import *
from datetime import datetime
import matplotlib.pyplot as plt

master = RS485_RTU_Master(1, baudrate = 9600, parity = 'E', stopbits = 1)
fig, ax = plt.subplots()
active_power = []
time = []
for i in range(0, 1000):
    start_time = datetime.now()
    time.append(i/10)
    try:
        read = master.read_multiple_holding_registers(1, int(0x140), 2)
    except Modbus_Exception:
        pass
    active_power.append(read[0]*int(0x10000)+read[1])
    ax.clear()
    ax.plot(time, active_power)
    while ((datetime.now()-start_time).total_seconds()) < 0.1 :
        sleep(0.01)
plt.show()

    
