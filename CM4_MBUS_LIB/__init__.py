import logging
from .RS485_Exceptions import *
from .Scanner import Scanner
from .RS485_RTU_Master import RS485_RTU_Master

logging.basicConfig(level=logging.DEBUG, filename='log.log', filemode='w', 
                    format="%(asctime)s - %(levelname)s - %(message)s")