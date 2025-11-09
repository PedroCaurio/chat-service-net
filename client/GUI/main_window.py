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

        self.show_login_screen()

    def show_login_screen(self):
        self.stacked_widget.setCurrentWidget(self.login_screen)
    
    def show_chat_screen(self, user_id):
        self.chat_screen.load_user(user_id)
        self.stacked_widget.setCurrentWidget(self.chat_screen)