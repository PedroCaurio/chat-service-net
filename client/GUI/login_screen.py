'''
Tela para login e registro (n conseguimos implementar o registro)
'''
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt

class LoginScreen(QWidget):
    login_requested = pyqtSignal(str, str)
    register_requested = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        login_box_layout = QVBoxLayout()
        login_box_layout.setContentsMargins(20, 20, 20, 20)

        self.label_title = QLabel("Bem vindo")
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_user = QLabel("Usuário:")
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Digite seu usuário")

        self.label_pass = QLabel("Senha:")
        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("Digite sua senha")
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)

        button_layout = QHBoxLayout()
        self.btn_login = QPushButton("Login")
        self.btn_register = QPushButton("Registrar")
        button_layout.addWidget(self.btn_login)
        button_layout.addWidget(self.btn_register)

        login_box_layout.addWidget(self.label_title)
        login_box_layout.addWidget(self.label_user)
        login_box_layout.addWidget(self.input_user)
        login_box_layout.addWidget(self.label_pass)
        login_box_layout.addWidget(self.input_pass)
        login_box_layout.addLayout(button_layout)

        main_layout.addLayout(login_box_layout)
        main_layout.addStretch()

        self.setLayout(main_layout)
        self.btn_login.clicked.connect(self.on_login_clicked)
        self.btn_register.clicked.connect(self.on_register_clicked)

    def on_login_clicked(self):
        username = self.input_user.text()
        password = self.input_pass.text()

        if username and password:
            print("tem login")
            self.login_requested.emit(username, password)
        else:
            self.show_error("Preencha todos os campos.")
    
    def on_register_clicked(self):
        username = self.input_user.text()
        password = self.input_pass.text()

        self.register_requested.emit(username, password)
        
    def show_error(self, message):
        QMessageBox.warning(self, "Erro", message)