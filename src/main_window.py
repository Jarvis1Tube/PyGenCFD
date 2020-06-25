import enum
import logging
import os
import sys
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import sympy
from PyQt5 import QtCore, QtWidgets

from generated.UI import Ui_MainWindow

import models.coordinate_systems as cs
from codegen.template_gen import gen_template
from models import problem
from tecplot_reader import read_tecplot

logger = logging.getLogger(__name__)


class FormulasState(enum.Enum):
    Text = "Text"
    Pretty = "Pretty"
    Undefined = "Undefined"


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._setup_events()
        self._setup_variables()

    def _setup_variables(self):
        self.strs_problem_model = problem.StrsModelsFromLabs["2.1"]
        self.FormulasState = FormulasState.Undefined
        self.ShowTextAction()

    # region property
    @property
    def Equation(self) -> str:
        return self.ui.EquationText.toPlainText()

    @Equation.setter
    def Equation(self, val: str):
        self.ui.EquationText.setPlainText(val)

    @property
    def CoordinateSystem(self) -> Optional[cs.CoordinateSystem]:
        current_cs = self.ui.CoordinateSystemCombo.currentText()
        if not current_cs:
            return None
        return cs.CoordinateSystem.from_str(current_cs)

    @CoordinateSystem.setter
    def CoordinateSystem(self, val: cs.CoordinateSystem):
        self.ui.IsStationaryCheckBox.setChecked(val.is_stationary())
        self.ui.DimensionsCountSpin.setValue(val.dimensions_count())
        cords_systems = cs.CoordinateSystem.filtered(
            is_stationary=val.is_stationary(), dimensions_count=val.dimensions_count()
        )
        current_cs = self.ui.CoordinateSystemCombo.setCurrentIndex(
            cords_systems.index(val)
        )

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

    @InitialCondition.setter
    def InitialCondition(self, val: str):
        self.ui.InitialConditionText.setPlainText(val)

    @property
    def LBoundaryConditions(self) -> List[str]:
        return self.GetBoundaryConditionsLR()[0]

    @LBoundaryConditions.setter
    def LBoundaryConditions(self, val: List[str]):
        self.SetBoundaryConditionsLR(L=val)

    @property
    def RBoundaryConditions(self) -> List[str]:
        return self.GetBoundaryConditionsLR()[1]

    @RBoundaryConditions.setter
    def RBoundaryConditions(self, val: List[str]):
        self.SetBoundaryConditionsLR(R=val)

    def GetBoundaryConditionsLR(self) -> Tuple[List[str], List[str]]:
        conditions: List[QtWidgets.QGroupBox] = [
            widget
            for widget in self.ui.BoudaryConditionsGroup.children()
            if type(widget) is not QtWidgets.QGridLayout
        ]
        L, R = [], []
        for cond_group in conditions:
            cond_text = GetTextFromGroup(cond_group)
            if "левый" in cond_group.title():
                L.append(cond_text.toPlainText())
            elif "правый" in cond_group.title():
                R.append(cond_text.toPlainText())
        if len(L) != len(R):
            logger.warning("Count of left and right boundary conditions not match")
        return L, R

    @property
    def AnalyticalSolution(self) -> Optional[str]:
        if not self.ui.AnalyticalSolutionGroup.isVisible:
            return None
        return self.ui.AnalyticalSolutionPlainText.toPlainText()

    @AnalyticalSolution.setter
    def AnalyticalSolution(self, val: str):
        self.ui.AnalyticalSolutionPlainText.setPlainText(val)

    def SetBoundaryConditionsLR(self, L=None, R=None) -> Tuple[List[str], List[str]]:
        insert_col = list(L or R or [])[::-1]
        search_word = "левый" if L else ("правый" if R else "abracadabra")

        if search_word == "abracadabra":
            logger.warning("SetBoundaryConditionsLR has no arguments!")

        conditions: List[QtWidgets.QGroupBox] = [
            widget
            for widget in self.ui.BoudaryConditionsGroup.children()
            if type(widget) is not QtWidgets.QGridLayout
        ]

        if (len(conditions) // 2) != len(
            insert_col
        ) and self.FormulasState != FormulasState.Undefined:
            logger.warning(
                "Boundary conditions setter has not exact count of conditions"
            )

        for cond_group in conditions:
            cond_text = GetTextFromGroup(cond_group)
            if not insert_col:
                break
            if search_word in cond_group.title():
                cond_text.setPlainText(insert_col.pop())
        return L, R

    # endregion property

    # region Events
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
        self.ui.ShowTextMenuButton.triggered.connect(self.ShowTextAction)
        self.ui.ShowPrettyMenuButton.triggered.connect(self.ShowPrettyAction)
        self.ui.HasAnaliticalCheckBox.stateChanged.connect(self.HasAnalitycalChanched)
        self.ui.CodeRunButton.clicked.connect(self.RunCode)
        self.ui.GraphsShowButton.clicked.connect(self.ShowGraphs)

    def SetUpBoundaryConditions(self):
        if self.CoordinateSystem:
            self._GenConditionsPlaceHolders(self.CoordinateSystem)
        self.ui.InitialConditionGroup.setVisible(not self.IsStationary)

    def SetUpCoordinateSystemCombo(self):
        coordinate_systems = cs.CoordinateSystem.filtered(
            self.DimensionCount, self.IsStationary
        )
        if len(coordinate_systems) == 0:
            if self.DimensionCount == 0:
                self.ui.DimensionsCountSpin.setValue(1)
            else:
                self.ui.DimensionsCountSpin.setValue(self.DimensionCount - 1)
            return

        if self.FormulasState == FormulasState.Pretty:
            self.ShowTextAction()

        self.ui.CoordinateSystemCombo.clear()
        self.ui.CoordinateSystemCombo.addItems([cs.value for cs in coordinate_systems])

        self.FormulasState = FormulasState.Undefined
        self.ShowTextAction()

    def ShowTextAction(self):
        if self.FormulasState == FormulasState.Text:
            return

        self.Equation = self.strs_problem_model.equation
        self.InitialCondition = self.strs_problem_model.initial_condition
        self.LBoundaryConditions = self.strs_problem_model.L_boundary_conditions
        self.RBoundaryConditions = self.strs_problem_model.R_boundary_conditions
        self.AnalyticalSolution = self.strs_problem_model.analytical_solution
        self.CoordinateSystem = self.strs_problem_model.coordinate_system

        self.FormulasState = FormulasState.Text

    def ShowPrettyAction(self):
        if self.FormulasState == FormulasState.Pretty:
            return

        self._UpdateStrsProblemModel()
        try:
            sympy_model = problem.ProblemSympy(self.strs_problem_model)
        except Exception as err:
            mbox = QtWidgets.QMessageBox(self)
            mbox.setIcon(mbox.Warning)
            mbox.setText(str(err))
            mbox.show()
            return

        self.Equation = sympy.pretty(sympy_model.equation)
        self.InitialCondition = sympy.pretty(sympy_model.initial_condition)
        self.LBoundaryConditions = [
            sympy.pretty(cond) for cond in sympy_model.L_boundary_conditions
        ]
        self.RBoundaryConditions = [
            sympy.pretty(cond) for cond in sympy_model.R_boundary_conditions
        ]
        self.AnalyticalSolution = sympy.pretty(sympy_model.analytical_solution)

        self.FormulasState = FormulasState.Pretty

    def HasAnalitycalChanched(self):
        self.ui.AnalyticalSolutionGroup.setVisible(
            self.ui.HasAnaliticalCheckBox.isChecked()
        )

    def GenerateCode(self):
        self._UpdateStrsProblemModel()
        grid_params = problem.GridParams(
            x_step=self.ui.XGridStepSpin.value(), t_step=self.ui.tGridStepSpin.value()
        )
        sympy_model = problem.ProblemSympy(self.strs_problem_model, grid_params)
        try:
            gen_template(sympy_model)
        except Exception as err:
            mbox = QtWidgets.QMessageBox(self)
            mbox.setIcon(mbox.Warning)
            mbox.setText(str(err))
        else:
            mbox = QtWidgets.QMessageBox(self)
            mbox.setIcon(mbox.Information)
            mbox.setText(f"Program successfully generated.")
        mbox.show()

    def RunCode(self):
        code_file = os.path.abspath("./src/generated/fortran_solver.f95")
        if not os.path.exists(code_file):
            mbox = QtWidgets.QMessageBox(self)
            mbox.setIcon(mbox.Warning)
            mbox.setText(
                f"Cannot find file {code_file}. May be you didn't run code generation."
            )
            mbox.show()
        status = os.system(f"cd ./src/generated/ && gfortran {code_file} && ./a.out")
        if status == 0:
            mbox = QtWidgets.QMessageBox(self)
            mbox.setIcon(mbox.Information)
            mbox.setText(f"Program successfully finished.")
        else:
            mbox = QtWidgets.QMessageBox(self)
            mbox.setIcon(mbox.Warning)
            mbox.setText(f"Program failed.")
        mbox.show()

    def ShowGraphs(self):
        ALL_DAT = os.path.abspath("./src/generated/ALL.DAT")
        if not os.path.exists(ALL_DAT):
            mbox = QtWidgets.QMessageBox(self)
            mbox.setIcon(mbox.Warning)
            mbox.setText(f"Cannot find file {ALL_DAT}. May be you didn't run code.")
            mbox.show()

        data = read_tecplot(ALL_DAT, verbose=False)[1][0]

        fig, (ax1, ax2, ax3) = plt.subplots(
            1, 3, figsize=(12, 4),  # gridspec_kw={"wspace": 0.35}
        )
        ax1.plot(data["X"], data["T"])
        ax1.set_title("Численное решение")
        ax1.set_xlabel("X")
        ax1.set_ylabel("Т (поле температуры)")

        ax2.plot(data["X"], data["Ta"])
        ax2.set_title("Аналитическое решение")
        ax2.set_xlabel("X")
        ax2.set_ylabel("Тa (аналитика)")

        ax3.plot(data["X"], (data["T"] - data["Ta"]).abs())
        ax3.set_title("Абсолютная погрешность")
        ax3.set_xlabel("X")
        ax3.set_ylabel("|T - Ta|")
        plt.tight_layout()

        plt.show()

    # endregion Events

    # region UI logic
    def _GenConditionsPlaceHolders(self, coordinate_systems: cs.CoordinateSystem):
        coinditions: QtWidgets.QGridLayout = self.ui.BoudaryConditionsGroup.layout()
        widgets = [
            w
            for w in self.ui.BoudaryConditionsGroup.children()
            if type(w) is not QtWidgets.QGridLayout
        ]
        for w in widgets:
            w.setParent(None)

        for cs_variable in coordinate_systems.value.replace("t", ""):
            for edge_name in ["левый", "правый"]:
                ConditionGroup = QtWidgets.QGroupBox(self.ui.BoudaryConditionsGroup)
                ConditionGroup.setTitle(f"{cs_variable} ({edge_name} конец)")
                verticalLayout = QtWidgets.QVBoxLayout(ConditionGroup)
                ConditionText = QtWidgets.QPlainTextEdit(ConditionGroup)
                ConditionText.setMaximumSize(QtCore.QSize(16777215, 80))
                verticalLayout.addWidget(ConditionText)

        widgets = [
            w
            for w in self.ui.BoudaryConditionsGroup.children()
            if type(w) is not QtWidgets.QGridLayout
        ]
        for i, widget in enumerate(widgets):
            coinditions.addWidget(widget, *(i // 2, i % 2))

    def _UpdateStrsProblemModel(self):
        self.strs_problem_model.equation = self.Equation
        self.strs_problem_model.initial_condition = self.InitialCondition
        self.strs_problem_model.L_boundary_conditions = self.LBoundaryConditions
        self.strs_problem_model.R_boundary_conditions = self.RBoundaryConditions
        self.strs_problem_model.analytical_solution = self.AnalyticalSolution
        self.strs_problem_model.coordinate_system = self.CoordinateSystem

    #  endregion UI logic


def GetTextFromGroup(group: QtWidgets.QGroupBox) -> QtWidgets.QPlainTextEdit:
    for child in group.children():
        if hasattr(child, "toPlainText"):
            return child
