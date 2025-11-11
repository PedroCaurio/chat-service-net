'''
Permite apenas uma tela por vez
'''

from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from .login_screen import LoginScreen
from .chat_screen import ChatScreen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat de Redes")
        self.setGeometry(100, 100, 800, 600)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.login_screen = LoginScreen()
        self.chat_screen = ChatScreen()

        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.chat_screen)
        
        self.show_login_screen()
        #self.show_chat_screen("asfg") # Botei o user id que tinha no meu db


    def show_login_screen(self):
        self.stacked_widget.setCurrentWidget(self.login_screen)
    
    def show_chat_screen(self, user_id, users):
        self.chat_screen.load_user_data(user_id, users)
        self.stacked_widget.setCurrentWidget(self.chat_screen)