# src/ui/error_report_dialog.py
"""
치명적 오류 발생 시 표시하는 '오류 보고창'. 내용 복사 가능.
"""
import sys
import traceback

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication


def format_exception(exc_type, exc_value, exc_tb) -> str:
    """예외 타입·메시지·트레이스백을 한 문자열로."""
    lines = traceback.format_exception(exc_type, exc_value, exc_tb)
    return "".join(lines)


class ErrorReportDialog(QDialog):
    """오류 내용을 보여 주고 클립보드로 복사할 수 있는 다이얼로그."""

    def __init__(self, exc_type, exc_value, exc_tb, parent=None):
        super().__init__(parent)
        self.setWindowTitle("오류 보고")
        self.setMinimumSize(500, 400)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("예기치 않은 오류가 발생했습니다. 아래 내용을 복사해 개발자에게 전달하세요."))
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setPlainText(format_exception(exc_type, exc_value, exc_tb))
        layout.addWidget(self.text)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        copy_btn = QPushButton("복사")
        copy_btn.clicked.connect(self._copy_to_clipboard)
        close_btn = QPushButton("닫기")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(copy_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def _copy_to_clipboard(self) -> None:
        clipboard = QGuiApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(self.text.toPlainText())


def exception_handler(exc_type, exc_value, exc_tb):
    """sys.excepthook 용: 치명적 예외 시 오류 보고창 표시. 프로그램은 종료하지 않음."""
    if exc_type is KeyboardInterrupt:
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    dlg = ErrorReportDialog(exc_type, exc_value, exc_tb)
    dlg.exec()
    # __excepthook__ 호출하지 않음 → 프로그램 유지, 사용자가 닫기 후 계속 사용 가능
