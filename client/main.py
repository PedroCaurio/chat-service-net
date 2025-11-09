import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread

from gui.main_window import MainWindow
from client_service import ClientService

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()
    worker_thread = QThread()
    worker_thread.setObjectName("ClientThread")

    client_service = ClientService()
    client_service.moveToThread(worker_thread)

    worker_thread.started.connect(client_service.connect)

    client_service.connection_error.connect(main_window.login_screen.show_error)
    client_service.connection_error.connect(main_window.show_login_screen)

    main_window.login_screen.login_requested.connect(client_service.try_login)
    client_service.login_sucess.connect(main_window.show_chat_screen)

    client_service.login_failed.connect(main_window.login_screen.show_error)

    # main_window.chat_screen.messsage_sended.connect(client_service.send_private_message)
    
    # client_service.new_message_received.connect(main_window.chat_screen.add_message)
    
    worker_thread.start()
    main_window.show()

    sys.exit(app.exec())