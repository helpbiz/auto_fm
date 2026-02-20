# src/main.py
import sys
import logging

from src.domain.migration_runner import run_migrations
from src.domain.db import get_connection
from src.domain.masterdata.service import apply_seed_if_needed
from src.utils.path_helper import get_logs_dir

try:
    from PyQt6.QtWidgets import QApplication
except ImportError:
    from PyQt5.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.ui.theme import get_global_stylesheet
from src.ui.error_report_dialog import exception_handler


def _setup_file_logging():
    """로그를 파일에 기록 (UTF-8 BOM). 로그 확인: 앱 실행 폴더 아래 logs/app.log 를 UTF-8로 열면 됨."""
    log_dir = get_logs_dir()
    log_file = log_dir / "app.log"
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    if not any(isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", "").endswith("app.log") for h in root.handlers):
        # utf-8-sig: BOM 추가 → Windows 메모장 등에서 한글이 깨지지 않고 열림
        fh = logging.FileHandler(log_file, encoding="utf-8-sig")
        fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
        root.addHandler(fh)
    return str(log_file)


def main():
    # 로그 파일 설정 (logs/app.log). 확인 방법은 아래 주석 참고.
    log_path = _setup_file_logging()
    logging.info("앱 시작. 로그 파일: %s", log_path)

    run_migrations()

    # 초기 마스터 데이터 생성 (처음 실행 시)
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
