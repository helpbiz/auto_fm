"""
Entry point: 4-step workflow app.
PyInstaller-friendly: no dynamic imports; stable relative paths.
Run from project root: python -m app.main
"""
import sys
import logging

from src.domain.migration_runner import run_migrations
from src.domain.db import get_connection
from src.domain.masterdata.service import apply_seed_if_needed

try:
    from PyQt6.QtWidgets import QApplication
except ImportError:
    from PyQt5.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.ui.theme import get_global_stylesheet
from src.ui.error_report_dialog import exception_handler


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    run_migrations()
    conn = get_connection()
    try:
        apply_seed_if_needed(conn)
    finally:
        conn.close()
    sys.excepthook = exception_handler
    app = QApplication([])
    app.setStyleSheet(get_global_stylesheet())
    window = MainWindow()
    window.resize(1200, 700)
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
