from typing import List

from generated.UI import Ui_MainWindow

from PyQt5 import QtWidgets, QtCore

import models


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._setup_events()

    def _setup_events(self):
        self.ui.GenerateCodeButton.clicked.connect(self.GenerateCode)

        self.ui.DimensionsCountSpin.valueChanged.connect(
            self.SetUpCoordinateSystemCombo
        )
        self.ui.IsStationaryCheckBox.stateChanged.connect(
            self.SetUpCoordinateSystemCombo
        )

        self.ui.CoordinateSystemCombo.currentTextChanged.connect(
            self.SetUpBoundaryConditions
        )

    def _GenConditionsPlaceHolders(self, coordinate_systems: models.CoordinateSystem):
        for cs_variable in coordinate_systems.value.replace("t", ""):
            for edge_name in ["левый", "правый"]:
                ConditionGroup = QtWidgets.QGroupBox(self.ui.BoudaryConditionsGroup)
                ConditionGroup.setTitle(f"{cs_variable} ({edge_name} конец)")
                verticalLayout = QtWidgets.QVBoxLayout(ConditionGroup)
                ConditionText = QtWidgets.QPlainTextEdit(ConditionGroup)
                ConditionText.setMaximumSize(QtCore.QSize(16777215, 80))
                verticalLayout.addWidget(ConditionText)

        coinditions: QtWidgets.QGridLayout = self.ui.BoudaryConditionsGroup.layout()
        widgets = [
            w
            for w in self.ui.BoudaryConditionsGroup.children()
            if type(w) is not QtWidgets.QGridLayout
        ]
        for i in reversed(range(coinditions.count())):
            coinditions.itemAt(i).widget().deleteLater()

        for i, widget in enumerate(widgets):
            coinditions.addWidget(widget, *(i // 2, i % 2))

    def SetUpBoundaryConditions(self):
        current_cs = self.ui.CoordinateSystemCombo.currentText()
        if not current_cs:
            return

        coordinate_system = models.CoordinateSystem.from_str(current_cs)
        self._GenConditionsPlaceHolders(coordinate_system)

    def SetUpCoordinateSystemCombo(self):
        dimension_count = int(self.ui.DimensionsCountSpin.value())
        is_stationary = bool(self.ui.IsStationaryCheckBox.isChecked())

        coordinate_systems = models.CoordinateSystem.filtered(
            dimension_count, is_stationary
        )
        if len(coordinate_systems) == 0:
            if dimension_count == 0:
                self.ui.DimensionsCountSpin.setValue(1)
            else:
                self.ui.DimensionsCountSpin.setValue(dimension_count - 1)
            return

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
