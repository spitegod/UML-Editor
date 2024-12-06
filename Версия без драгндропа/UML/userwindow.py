import os
import json
import sys
import subprocess
from PyQt5 import QtWidgets


class LoginWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход или регистрация")
        self.setGeometry(100, 100, 300, 200)

        # Папка для хранения данных пользователей
        self.user_data_folder = "user_data"
        os.makedirs(self.user_data_folder, exist_ok=True)

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

        user_file = os.path.join(self.user_data_folder, f"{username}.json")
        if os.path.exists(user_file):
            with open(user_file, "r") as f:
                user_data = json.load(f)

            if user_data.get("password") == password:
                QtWidgets.QMessageBox.information(self, "Успех", f"Добро пожаловать, {username}!")
                self.accept()  # Закрыть окно с результатом успешного входа
                self.launch_editor()  # Запуск редактора после успешного входа
            else:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Неверный пароль!")
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Пользователь не найден!")

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Простая проверка валидности ввода
        if len(username) > 3 and len(password) > 3:
            user_file = os.path.join(self.user_data_folder, f"{username}.json")

            if os.path.exists(user_file):
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Пользователь с таким именем уже существует!")
                return

            user_data = {
                "username": username,
                "password": password
            }

            with open(user_file, "w") as f:
                json.dump(user_data, f)

            QtWidgets.QMessageBox.information(self, "Успех", "Пользователь успешно зарегистрирован!")
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Логин и пароль должны быть длиннее 3 символов!")

    def launch_editor(self):
        try:
            # Запуск файла uml_editor.py
            current_dir = os.path.dirname(os.path.abspath(__file__))
            uml_editor_path = os.path.join(current_dir, 'umleditor.py')
            
            # Используем subprocess.call() для блокирующего запуска
            subprocess.call(['python', uml_editor_path])  # Это блокирует программу до завершения редактора

            # После выполнения редактора, завершение приложения
            QtWidgets.QApplication.quit()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось запустить UML Editor: {e}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    login_window = LoginWindow()

    # После завершения окна входа, закрываем приложение
    if login_window.exec_() == QtWidgets.QDialog.Accepted:
        print("Вход выполнен!")
    
    # Завершаем приложение после выполнения всех действий (включая неудачный вход)
    app.quit()  # Завершаем приложение, независимо от того, был ли успешный вход или нет
