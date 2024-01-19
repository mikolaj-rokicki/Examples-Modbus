from Classes.App import App



if __name__ == '__main__':
    DEVICE_ADDRESSES = [10, 16, 18]
    REGISTER_ADDRESSES = [[0], [0, 1], [0, 10]]
    myApp = App(True, False, False, DEVICE_ADDRESSES, REGISTER_ADDRESSES)




        