from generated.UI import Ui_MainWindow

from PyQt5 import QtWidgets


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._setup_events()

    def _setup_events(self):
        self.ui.GenerateCodeButton.clicked.connect(self.GenerateCode)

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
