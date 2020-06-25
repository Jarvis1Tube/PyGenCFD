import filecmp

from PyQt5 import QtWidgets

import problem
from main_window import MainWindow


def test_codegen_not_fails():
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.GenerateCode()
