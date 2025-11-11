# client/main.py
#
#       TRABALHO EM ANDAMENTO - MTA IA AINDA
#

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread
from client_service import ClientService 
from gui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()
    worker_thread = QThread()
    worker_thread.setObjectName("ClientThread")
    client_service = ClientService(main_window)
    client_service.moveToThread(worker_thread)

    worker_thread.started.connect(client_service.connect_and_listen)


    worker_thread.start()
    main_window.show()

    sys.exit(app.exec())