# src/main.py
from src.domain.migration_runner import run_migrations

try:
    from PyQt6.QtWidgets import QApplication
except ImportError:
    from PyQt5.QtWidgets import QApplication

from src.ui.main_window import MainWindow


def main():
    run_migrations()
    app = QApplication([])
    window = MainWindow()
    window.resize(900, 420)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
