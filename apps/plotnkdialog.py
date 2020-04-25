# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plotnkdialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog_NKplot(object):
    def setupUi(self, Dialog_NKplot):
        Dialog_NKplot.setObjectName("Dialog_NKplot")
        Dialog_NKplot.resize(831, 556)
        self.gridLayout = QtWidgets.QGridLayout(Dialog_NKplot)
        self.gridLayout.setObjectName("gridLayout")
        self.listWidget_nkplot = QtWidgets.QListWidget(Dialog_NKplot)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget_nkplot.sizePolicy().hasHeightForWidth())
        self.listWidget_nkplot.setSizePolicy(sizePolicy)
        self.listWidget_nkplot.setObjectName("listWidget_nkplot")
        self.gridLayout.addWidget(self.listWidget_nkplot, 0, 1, 1, 1)
        self.frame = QtWidgets.QFrame(Dialog_NKplot)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.widget_nkplot = QtWidgets.QWidget(self.frame)
        self.widget_nkplot.setObjectName("widget_nkplot")
        self.gridLayout_nkplot = QtWidgets.QGridLayout(self.widget_nkplot)
        self.gridLayout_nkplot.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_nkplot.setObjectName("gridLayout_nkplot")
        self.gridLayout_2.addWidget(self.widget_nkplot, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)

        self.retranslateUi(Dialog_NKplot)
        QtCore.QMetaObject.connectSlotsByName(Dialog_NKplot)

    def retranslateUi(self, Dialog_NKplot):
        _translate = QtCore.QCoreApplication.translate
        Dialog_NKplot.setWindowTitle(_translate("Dialog_NKplot", "Check the nk data"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog_NKplot = QtWidgets.QDialog()
    ui = Ui_Dialog_NKplot()
    ui.setupUi(Dialog_NKplot)
    Dialog_NKplot.show()
    sys.exit(app.exec_())

