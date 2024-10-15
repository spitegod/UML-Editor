
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(139, 136)
        self.gridLayout_2 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.pushButton_BGcolor = QtWidgets.QPushButton(Dialog)
        self.pushButton_BGcolor.setStyleSheet("background-color: rgb(255, 0, 0);")
        self.pushButton_BGcolor.setText("")
        self.pushButton_BGcolor.setObjectName("pushButton_BGcolor")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.pushButton_BGcolor)
        self.lineEdit_text = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_text.setText("")
        self.lineEdit_text.setObjectName("lineEdit_text")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_text)
        self.gridLayout.addLayout(self.formLayout, 1, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton_delete = QtWidgets.QPushButton(Dialog)
        self.pushButton_delete.setStyleSheet("color: rgb(255, 0, 0);")
        self.pushButton_delete.setObjectName("pushButton_delete")
        self.horizontalLayout_2.addWidget(self.pushButton_delete)
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setStyleSheet("background-color: rgb(117, 117, 117);")
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout_2.addWidget(self.line)
        self.pushButton_copy = QtWidgets.QPushButton(Dialog)
        self.pushButton_copy.setObjectName("pushButton_copy")
        self.horizontalLayout_2.addWidget(self.pushButton_copy)
        self.gridLayout.addLayout(self.horizontalLayout_2, 4, 0, 1, 1)
        self.line_2 = QtWidgets.QFrame(Dialog)
        self.line_2.setStyleSheet("background-color: rgb(117, 117, 117);")
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 3, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        
        # Подключение сигнала нажатия кнопки к слоту
        self.pushButton_BGcolor.clicked.connect(self.open_color_dialog)

        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Управление"))
        self.label_4.setText(_translate("Dialog", "Управление"))
        self.label.setText(_translate("Dialog", "Цвет"))
        self.label_2.setText(_translate("Dialog", "Tекст"))
        self.pushButton_delete.setText(_translate("Dialog", "Удалить"))
        self.pushButton_copy.setText(_translate("Dialog", "Копировать"))

    def open_color_dialog(self):
        # Открытие диалогового окна выбора цвета
        color = QtWidgets.QColorDialog.getColor()

        # Если цвет выбран, изменить цвет кнопки
        if color.isValid():
            self.pushButton_BGcolor.setStyleSheet(f"background-color: {color.name()};")


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
