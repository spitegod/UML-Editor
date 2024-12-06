import sys

from PyQt5 import QtWidgets, QtGui

class LoginWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход или регистрация")
        self.setGeometry(100, 100, 300, 200)

        # Лейауты
        layout = QtWidgets.QVBoxLayout(self)

        # Поля ввода
        self.username_input = QtWidgets.QLineEdit(self)
        self.username_input.setPlaceholderText("Введите логин")
        self.password_input = QtWidgets.QLineEdit(self)
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        # Кнопки
        self.login_button = QtWidgets.QPushButton("Войти", self)
        self.register_button = QtWidgets.QPushButton("Зарегистрироваться", self)

        # Добавление виджетов в лейаут
        layout.addWidget(QtWidgets.QLabel("Авторизация", self))
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        # Связывание кнопок с методами
        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Пример проверки (можно заменить на запрос в базу данных)
        if username == "admin" and password == "1234":
            QtWidgets.QMessageBox.information(self, "Успех", "Вы вошли в систему!")
            self.accept()  # Закрыть окно с результатом успешного входа
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Простая проверка валидности ввода
        if len(username) > 3 and len(password) > 3:
            QtWidgets.QMessageBox.information(self, "Регистрация", "Пользователь успешно зарегистрирован!")
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Логин и пароль должны быть длиннее 3 символов!")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)  # Создаем экземпляр приложения
    login_window = LoginWindow()  # Создаем окно авторизации

    # Показываем окно и проверяем результат
    if login_window.exec_() == QtWidgets.QDialog.Accepted:
        print("Вход выполнен!")  # Здесь можно запустить главное окно приложения

    sys.exit(app.exec_())  # Запускаем цикл обработки событий