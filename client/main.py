import sys
from PyQt6.QtWidgets import QApplication
from client_back.client_service import ClientService 
from GUI.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    client_service = ClientService(main_window)
    main_window.show()

    sys.exit(app.exec())