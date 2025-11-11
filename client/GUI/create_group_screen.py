'''
Tela para criação dos grupos
'''

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt

class CreateGroupScreen(QWidget):
    create_group_requested = pyqtSignal(str, str, str)
    return_requested = pyqtSignal(str, dict)

    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        login_box_layout = QVBoxLayout()
        login_box_layout.setContentsMargins(20, 20, 20, 20)

        self.label_title = QLabel("Gerenciador de Grupos")
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label_group_name = QLabel("Nome do Grupo:")
        self.input_group = QLineEdit()
        self.input_group.setPlaceholderText("Digite o nome do grupo")

        self.label_user = QLabel("Usuário que quer convidar:")
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Digite o nome do usuário que deseja convidar")

        button_layout = QHBoxLayout()
        self.btn_send = QPushButton("Enviar")
        self.btn_return = QPushButton("Voltar")
        button_layout.addWidget(self.btn_send)
        button_layout.addWidget(self.btn_return)

        login_box_layout.addWidget(self.label_title)
        login_box_layout.addWidget(self.label_group_name)
        login_box_layout.addWidget(self.input_group)
        login_box_layout.addWidget(self.label_user)
        login_box_layout.addWidget(self.input_user)
        login_box_layout.addLayout(button_layout)

        main_layout.addLayout(login_box_layout)
        main_layout.addStretch()

        self.setLayout(main_layout)
        self.btn_send.clicked.connect(self.on_send_clicked)
        self.btn_return.clicked.connect(self.on_return_clicked)
    def associate_user(self, user, users):
        self.user_id = user
        self.users = users
    def on_send_clicked(self):
        group_name = self.input_group.text()
        user = self.input_user.text()

        if group_name and user:
            self.create_group_requested.emit(group_name, user, self.user_id)
        else:
            self.show_error("Preencha todos os campos.")
    
    def on_return_clicked(self):
        self.return_requested.emit(self.user_id, self.users)    

    def show_error(self, message):
        QMessageBox.warning(self, "Erro", message)