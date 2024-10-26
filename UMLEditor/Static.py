import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, QTime

class Ui_StaticWidget(object):  # Изменение имени класса на Ui_StaticWidget

    # def set_time(self, time_str):
    #     """Метод для установки времени в lineEdit_timework."""
    #     self.lineEdit_timework.setText(time_str)

    def setupUi(self, StaticWidget):  # Используем StaticWidget вместо StaticWindow

        import umleditor

        # Создаём экземпляр MainWindow и вызываем get_last_time()
        main_window = umleditor.Ui_MainWindow()  # Создаём экземпляр класса Ui_MainWindow

        StaticWidget.setObjectName("StaticWidget")
        StaticWidget.setWindowModality(QtCore.Qt.NonModal)
        StaticWidget.resize(316, 157)
        StaticWidget.setFixedSize(600, 250)  # Фиксируем размер окна
        
        self.gridLayout = QtWidgets.QGridLayout(StaticWidget)  # Основной layout для StaticWidget
        self.gridLayout.setObjectName("gridLayout")
        
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        
        # Заголовок "Статистика"
        # self.label = QtWidgets.QLabel(StaticWidget)
        # self.label.setObjectName("label")
        # self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        
        # Основная рабочая область
        self.horizontalLayout_workarea = QtWidgets.QHBoxLayout()
        self.horizontalLayout_workarea.setObjectName("horizontalLayout_workarea")
        
        # Блок выбора пользователя
        self.verticalLayout_UserChoose = QtWidgets.QVBoxLayout()
        self.verticalLayout_UserChoose.setObjectName("verticalLayout_UserChoose")
        
        self.label_2 = QtWidgets.QLabel(StaticWidget)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_UserChoose.addWidget(self.label_2)
        
        self.listWidget_Users = QtWidgets.QListWidget(StaticWidget)
        self.listWidget_Users.setObjectName("listWidget_Users")
        for username in ["User1"]:
            item = QtWidgets.QListWidgetItem(username)
            self.listWidget_Users.addItem(item)
        
        self.verticalLayout_UserChoose.addWidget(self.listWidget_Users)
        self.horizontalLayout_workarea.addLayout(self.verticalLayout_UserChoose)
        
        # Вторая половина интерфейса
        self.verticalLayout_2half = QtWidgets.QVBoxLayout()
        self.verticalLayout_2half.setObjectName("verticalLayout_2half")
        
        # Время работы, начало и конец
        self.gridLayout_1section = QtWidgets.QGridLayout()
        self.gridLayout_1section.setObjectName("gridLayout_1section")
        
        self.lineEdit_timework = QtWidgets.QLineEdit(StaticWidget)
        self.lineEdit_timework.setReadOnly(True)
        self.lineEdit_timework.setInputMask("00:00:00")
        self.lineEdit_timework.setObjectName("lineEdit_timework")
        self.gridLayout_1section.addWidget(self.lineEdit_timework, 2, 1, 1, 1)
        
        self.label_5 = QtWidgets.QLabel(StaticWidget)
        self.label_5.setObjectName("label_5")
        self.gridLayout_1section.addWidget(self.label_5, 1, 2, 1, 1)
        
        self.label_4 = QtWidgets.QLabel(StaticWidget)
        self.label_4.setObjectName("label_4")
        self.gridLayout_1section.addWidget(self.label_4, 1, 1, 1, 1)
        
        self.dateTimeEdit_Start = QtWidgets.QLineEdit(StaticWidget)
        self.dateTimeEdit_Start.setReadOnly(True)
        self.dateTimeEdit_Start.setObjectName("dateTimeEdit_Start")
        self.gridLayout_1section.addWidget(self.dateTimeEdit_Start, 2, 0, 1, 1)
        
        self.dateTimeEdit_End = QtWidgets.QLineEdit(StaticWidget)
        self.dateTimeEdit_End.setReadOnly(True)
        self.dateTimeEdit_End.setObjectName("dateTimeEdit_End")
        self.gridLayout_1section.addWidget(self.dateTimeEdit_End, 2, 2, 1, 1)
        
        self.label_3 = QtWidgets.QLabel(StaticWidget)
        self.label_3.setObjectName("label_3")
        self.gridLayout_1section.addWidget(self.label_3, 1, 0, 1, 1)
        
        self.verticalLayout_2half.addLayout(self.gridLayout_1section)
        
        # История действий
        self.label_6 = QtWidgets.QLabel(StaticWidget)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_2half.addWidget(self.label_6)
        
        self.tableWidget = QtWidgets.QTableWidget(StaticWidget)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(["Время", "Действие"])
        
        self.verticalLayout_2half.addWidget(self.tableWidget)
        self.horizontalLayout_workarea.addLayout(self.verticalLayout_2half)
        
        self.gridLayout_2.addLayout(self.horizontalLayout_workarea, 1, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 1)

        #self.lineEdit_timework.setText(self.last_time)
        self.lineEdit_timework.setText(main_window.get_last_time())  # Получаем время через экземпляр

        #Таймер

        #Инициализируем переменные для секундомера
        self.running = False
        self.elapsed_time = QTime(0, 0)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)

        #self.start()


        self.retranslateUi(StaticWidget)
        QtCore.QMetaObject.connectSlotsByName(StaticWidget)

    #Ниже 4 функции - реализация работы таймера

    def start(self):
        if not self.running:  # Запускаем таймер, только если он не запущен
            self.running = True
            self.timer.start(1000)  # Интервал 1000 мс (1 секунда)

    def stop(self):
        if self.running:  # Останавливаем таймер
            self.running = False
            self.timer.stop()

    def reset(self):
        self.elapsed_time = QTime(0, 0)  # Сбрасываем время
        self.lineEdit_timework.setText(self.elapsed_time.toString("hh:mm:ss"))  # Отображаем сброшенное время

    def update_time(self):
        self.elapsed_time = self.elapsed_time.addSecs(1)  # Увеличиваем время на 1 секунду
        self.lineEdit_timework.setText(self.elapsed_time.toString("hh:mm:ss"))  # Обновляем отображение времени
        self.dateTimeEdit_End.setText(self.elapsed_time.toString("00.00.0000 hh:mm:ss"))

    def update_timework(self, new_time):
        """Слот для приема нового времени и обновления lineEdit_timework."""
        self.lineEdit_timework.setText(new_time)

    def retranslateUi(self, StaticWidget):
        _translate = QtCore.QCoreApplication.translate
        StaticWidget.setWindowTitle(_translate("StaticWidget", "Статистика"))
        # self.label.setText(_translate("StaticWidget", "Статистика"))
        self.label_2.setText(_translate("StaticWidget", "Пользователь"))
        self.label_3.setText(_translate("StaticWidget", "Начало работы"))
        self.label_4.setText(_translate("StaticWidget", "Время работы"))
        self.label_5.setText(_translate("StaticWidget", "Конец работы"))
        self.label_6.setText(_translate("StaticWidget", "История действий"))
        self.lineEdit_timework.setText(_translate("StaticWidget", "00:00:00"))
        self.dateTimeEdit_Start.setInputMask(_translate("StaticWindow", "00.00.0000 00:00:00"))
        self.dateTimeEdit_Start.setText(_translate("StaticWindow", "00.00.0000 00:00:00"))
        self.dateTimeEdit_End.setInputMask(_translate("StaticWindow", "00.00.0000 00:00:00"))
        self.dateTimeEdit_End.setText(_translate("StaticWindow", "00.00.0000 00:00:00"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    StaticWidget = QtWidgets.QWidget()
    ui = Ui_StaticWidget()
    ui.setupUi(StaticWidget)
    StaticWidget.show()
    sys.exit(app.exec_())