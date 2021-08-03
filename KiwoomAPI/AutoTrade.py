import sys
from kiwoom.kiwoom import *
from PyQt5.QtWidgets import *


class Main:
    def __init__(self):
        symbol_list = []

        self.app = QApplication(sys.argv)
        self.kiwoom = Kiwoom()
        self.app.exec_()


if __name__ == "__main__":
    Main()
