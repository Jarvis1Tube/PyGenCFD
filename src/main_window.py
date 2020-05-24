from generated.UI import Ui_MainWindow

from PyQt5 import QtWidgets

import models


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._setup_events()

    def _setup_events(self):
        self.ui.GenerateCodeButton.clicked.connect(self.GenerateCode)

        self.ui.DimensionsCountSpin.valueChanged.connect(self.SetUpCoordinateSystem)
        self.ui.IsStationaryCheckBox.stateChanged.connect(self.SetUpCoordinateSystem)

    def SetUpCoordinateSystem(self):
        dimension_count = int(self.ui.DimensionsCountSpin.value())
        is_stationary = bool(self.ui.IsStationaryCheckBox.isChecked())

        coordinate_systems = models.CoordinateSystem.filtered(
            dimension_count, is_stationary
        )

        self.ui.CoordinateSystemCombo.clear()
        self.ui.CoordinateSystemCombo.addItems([cs.value for cs in coordinate_systems])

    def GenerateCode(self):
        info_mbox = QtWidgets.QMessageBox(self)
        info_mbox.setIcon(QtWidgets.QMessageBox.Information)
        info_mbox.setText(
            """
            Hello, I see you want to generate CFD code =)
            I really want it too!
            Hope you'll do it in the next version of application.
            """
        )
        info_mbox.show()

        equation_text: str = self.ui.EquationText.toPlainText()
        print(equation_text)
