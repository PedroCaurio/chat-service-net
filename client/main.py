'''
    Entrada do client. Cria a janela e o serviço principal do client
'''

import sys
from PyQt6.QtWidgets import QApplication
from client_back.client_service import ClientService 
from GUI.main_window import MainWindow
from client_back.data_helper import data_helper

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(data_helper.save_data)
    main_window = MainWindow()
    client_service = ClientService(main_window)
    main_window.show()

    sys.exit(app.exec())