from Classes.App import App
import sys


if __name__ == '__main__':
    WINDOWS = sys.platform == 'win32'
    DEVICE_ADDRESSES = [10, 16, 18]
    REGISTER_ADDRESSES = [[0], [0, 1], [0, 10]]
    myApp = App(WINDOWS, False, False, DEVICE_ADDRESSES, REGISTER_ADDRESSES)




        