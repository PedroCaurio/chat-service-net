# client/main.py
#
#       TRABALHO EM ANDAMENTO - MTA IA AINDA
#

import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QThread
from client_service import ClientService 
from GUI.main_window import MainWindow 

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()
    worker_thread = QThread()
    worker_thread.setObjectName("ClientThread")
    client_service = ClientService()
    client_service.moveToThread(worker_thread)

    worker_thread.started.connect(client_service.connect_and_listen)

    # --- Conexões de Login e Erro ---
    client_service.connection_error.connect(main_window.login_screen.show_error)
    client_service.connection_error.connect(main_window.show_login_screen)
    def on_disconnect():
        QMessageBox.warning(main_window, "Desconectado", "A conexão com o servidor foi perdida.")
        main_window.show_login_screen()
    client_service.server_disconnected.connect(on_disconnect)
    
    main_window.login_screen.login_requested.connect(client_service.try_login)
    
    client_service.login_sucess.connect(main_window.show_chat_screen)
    client_service.login_sucess.connect(main_window.chat_screen.load_user_data)
    
    client_service.login_failed.connect(main_window.login_screen.show_error)

    # --- Conexões de Chat (Envio) ---
    
    main_window.chat_screen.private_message_sended.connect(client_service.send_private_message)
    main_window.chat_screen.group_message_sended.connect(client_service.send_group_message)
    main_window.chat_screen.general_message_sended.connect(client_service.send_general_message)
    
    # --- Conexões de Chat (Recebimento) ---
    
    client_service.new_private_message.connect(main_window.chat_screen.add_private_message)
    client_service.new_group_message.connect(main_window.chat_screen.add_group_message)
    client_service.new_general_message.connect(main_window.chat_screen.add_general_message)

    worker_thread.start()
    main_window.show()

    sys.exit(app.exec())