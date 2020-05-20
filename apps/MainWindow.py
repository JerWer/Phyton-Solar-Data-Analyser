import sys
from PyQt5 import QtWidgets

from TMsimulNew_Pyth36PyQT5 import TMSimulation
from IVpyqt5 import IVapp
from EQEpyqt5 import EQEapp
from Spectropyqt5 import Spectroapp
from XRDpyqt5 import XRDapp

from PyQt5.uic import loadUiType
Ui_MainWindow, QMainWindow = loadUiType('MainGUI.ui')


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.ui.pushButton_SolarSim.clicked.connect(lambda: self.Launch(IVapp))
        self.ui.pushButton_uvspectro.clicked.connect(lambda: self.Launch(Spectroapp))
        self.ui.pushButton_TMM.clicked.connect(lambda: self.Launch(TMSimulation))
        self.ui.pushButton_EQE.clicked.connect(lambda: self.Launch(EQEapp))
        self.ui.pushButton_XRD.clicked.connect(lambda: self.Launch(XRDapp))
        
    def Launch(self, Appfunction):
        self.w = Appfunction()
        self.w.show()
        self.hide()

#%%#############
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())