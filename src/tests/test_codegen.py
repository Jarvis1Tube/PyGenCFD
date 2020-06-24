import filecmp

from PyQt5 import QtWidgets

from main_window import MainWindow


def test_codegen_not_fails():
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.GenerateCode()


def test_1dim_codegen():
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.GenerateCode()
    assert filecmp.cmp(
        "src/generated/fortran_solver.f95", "src/tests/static/1dim_1.1.f95"
    )
