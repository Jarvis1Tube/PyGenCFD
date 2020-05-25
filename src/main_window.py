from typing import List, Optional

from generated.UI import Ui_MainWindow

from PyQt5 import QtWidgets, QtCore

import models


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._setup_events()

    @property
    def Equation(self) -> str:
        return self.ui.EquationText.toPlainText()

    @property
    def CoordinateSystemSelected(self) -> Optional[models.CoordinateSystem]:
        current_cs = self.ui.CoordinateSystemCombo.currentText()
        if not current_cs:
            return None
        return models.CoordinateSystem.from_str(current_cs)

    @property
    def DimensionCount(self):
        return int(self.ui.DimensionsCountSpin.value())

    @property
    def IsStationary(self):
        return bool(self.ui.IsStationaryCheckBox.isChecked())

    @property
    def InitialCondition(self) -> Optional[str]:
        if not self.ui.InitialConditionGroup.isVisible:
            return None
        return self.ui.InitialConditionText.toPlainText()

    @property
    def BoundaryConditionsLR(self):
        conditions: List[QtWidgets.QGroupBox] = [
            widget
            for widget in self.ui.BoudaryConditionsGroup.children()
            if type(widget) is not QtWidgets.QGridLayout
        ]
        L, R = [], []
        for cond_group in conditions:
            cond_text = GetTextFromGroup(cond_group)
            if "левый" in cond_group.title():
                L.append(cond_text)
            elif "правый" in cond_group.title():
                R.append(cond_text)
        return L, R

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
        if self.CoordinateSystemSelected:
            self._GenConditionsPlaceHolders(self.CoordinateSystemSelected)
        self.ui.InitialConditionGroup.setVisible(not self.IsStationary)

    def SetUpCoordinateSystemCombo(self):
        coordinate_systems = models.CoordinateSystem.filtered(
            self.DimensionCount, self.IsStationary
        )
        if len(coordinate_systems) == 0:
            if self.DimensionCount == 0:
                self.ui.DimensionsCountSpin.setValue(1)
            else:
                self.ui.DimensionsCountSpin.setValue(self.DimensionCount - 1)
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

        if not self.CoordinateSystemSelected:
            return

        problem_model = models.ProblemModel(
            equation=self.Equation,
            L_boundary_conditions=self.BoundaryConditionsLR[0],
            R_boundary_conditions=self.BoundaryConditionsLR[1],
            initial_condition=self.InitialCondition,
            dimensions_count=self.DimensionCount,
            is_stationary=self.IsStationary,
            coordinate_system=self.CoordinateSystemSelected,
        )


def GetTextFromGroup(group: QtWidgets.QGroupBox):
    for child in group.children():
        if hasattr(child, "toPlainText"):
            return child.toPlainText()
    return None
