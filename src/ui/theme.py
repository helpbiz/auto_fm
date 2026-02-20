# src/ui/theme.py
"""
중앙 테마: 색상·타이포·간격·컴포넌트 QSS. 앱 전체에 일관된 전문 디자인 적용.
"""

# ---- 색상 팔레트 ----
COLOR_PRIMARY = "#1565c0"
COLOR_PRIMARY_HOVER = "#0d47a1"
COLOR_SECONDARY = "#546e7a"
COLOR_SUCCESS = "#2e7d32"
COLOR_ERROR = "#c62828"
COLOR_BG = "#f5f5f5"
COLOR_CARD_BG = "#ffffff"
COLOR_CARD_BORDER = "#e0e0e0"
COLOR_TEXT = "#1a1a1a"
COLOR_TEXT_MUTED = "#666666"
COLOR_TABLE_ALT = "#fafafa"
COLOR_HEADER_BG = "#eceff1"
COLOR_HEADER_BORDER = "#cfd8dc"
COLOR_INPUT_FOCUS = COLOR_PRIMARY
COLOR_VALIDATION_ERROR = COLOR_ERROR
COLOR_VALIDATION_ERROR_BG = "#ffebee"

# ---- 타이포 ----
FONT_FAMILY = "Segoe UI, Malgun Gothic, sans-serif"
FONT_SIZE_BASE = "13px"
FONT_SIZE_SECTION = "14px"
FONT_SIZE_CAPTION = "11px"
FONT_SIZE_CARD_VALUE = "14px"
FONT_WEIGHT_BOLD = "bold"

# ---- 간격 ----
SPACING_UNIT = 8
CARD_PADDING = 12
SECTION_MARGIN = 12
BUTTON_SPACING = 6
FORM_SPACING = 6

# ---- 카드 (SummaryPanel 등) ----
CARD_STYLE = f"""
    QFrame {{
        background-color: {COLOR_CARD_BG};
        border: 1px solid {COLOR_CARD_BORDER};
        border-radius: 8px;
        padding: {CARD_PADDING}px;
    }}
"""
CARD_TITLE_STYLE = f"color: {COLOR_TEXT_MUTED}; font-size: {FONT_SIZE_CAPTION};"
CARD_VALUE_STYLE = f"font-weight: {FONT_WEIGHT_BOLD}; font-size: {FONT_SIZE_CARD_VALUE}; color: {COLOR_TEXT};"
CARD_VALUE_SUCCESS = f"font-weight: {FONT_WEIGHT_BOLD}; font-size: {FONT_SIZE_CARD_VALUE}; color: {COLOR_SUCCESS};"
CARD_VALUE_ERROR = f"font-weight: {FONT_WEIGHT_BOLD}; font-size: {FONT_SIZE_CARD_VALUE}; color: {COLOR_ERROR};"

# ---- 섹션 제목 ----
SECTION_TITLE_STYLE = f"font-weight: {FONT_WEIGHT_BOLD}; font-size: {FONT_SIZE_SECTION}; color: {COLOR_TEXT};"

# ---- 검증 (validation.py) ----
STYLE_VALID = ""
STYLE_INVALID = f"border: 2px solid {COLOR_VALIDATION_ERROR};"

# ---- 전체 앱 QSS ----
def get_global_stylesheet() -> str:
    return f"""
    QWidget {{
        background-color: {COLOR_BG};
        font-family: {FONT_FAMILY};
        font-size: {FONT_SIZE_BASE};
        color: {COLOR_TEXT};
    }}
    QMainWindow, QDialog {{
        background-color: {COLOR_BG};
    }}
    QMenuBar {{
        background-color: {COLOR_CARD_BG};
        border-bottom: 1px solid {COLOR_CARD_BORDER};
        padding: 4px 0;
    }}
    QMenuBar::item:selected {{
        background-color: {COLOR_HEADER_BG};
        border-radius: 4px;
    }}
    QPushButton {{
        background-color: {COLOR_SECONDARY};
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 14px;
        font-weight: bold;
        min-height: 20px;
    }}
    QPushButton:hover {{
        background-color: #455a64;
    }}
    QPushButton:pressed {{
        background-color: #37474f;
    }}
    QPushButton:disabled {{
        background-color: #b0bec5;
        color: #eceff1;
    }}
    QPushButton[class="primary"] {{
        background-color: {COLOR_PRIMARY};
    }}
    QPushButton[class="primary"]:hover {{
        background-color: {COLOR_PRIMARY_HOVER};
    }}
    QPushButton[class="primary"]:pressed {{
        background-color: #0d47a1;
    }}
    QLineEdit, QComboBox {{
        background-color: {COLOR_CARD_BG};
        border: 1px solid {COLOR_CARD_BORDER};
        border-radius: 4px;
        padding: 6px 10px;
        min-height: 20px;
        selection-background-color: {COLOR_PRIMARY};
    }}
    QLineEdit:focus, QComboBox:focus {{
        border: 1px solid {COLOR_INPUT_FOCUS};
    }}
    QComboBox::drop-down {{
        border: none;
        padding-right: 8px;
    }}
    QTableWidget {{
        background-color: {COLOR_CARD_BG};
        gridline-color: {COLOR_CARD_BORDER};
        border: 1px solid {COLOR_CARD_BORDER};
        border-radius: 6px;
    }}
    QTableWidget::item {{
        padding: 6px 8px;
    }}
    QTableWidget::item:alternate {{
        background-color: {COLOR_TABLE_ALT};
    }}
    QHeaderView::section {{
        background-color: {COLOR_HEADER_BG};
        color: {COLOR_TEXT};
        padding: 8px 10px;
        border: none;
        border-bottom: 2px solid {COLOR_HEADER_BORDER};
        border-right: 1px solid {COLOR_HEADER_BORDER};
        font-weight: bold;
    }}
    QHeaderView::section:first {{
        border-top-left-radius: 5px;
    }}
    QTabWidget::pane {{
        border: 1px solid {COLOR_CARD_BORDER};
        border-radius: 6px;
        background-color: {COLOR_CARD_BG};
        top: -1px;
    }}
    QTabBar::tab {{
        background-color: {COLOR_HEADER_BG};
        color: {COLOR_TEXT};
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }}
    QTabBar::tab:selected {{
        background-color: {COLOR_CARD_BG};
        border: 1px solid {COLOR_CARD_BORDER};
        border-bottom: none;
    }}
    QTabBar::tab:hover:!selected {{
        background-color: #e0e0e0;
    }}
    QLabel {{
        color: {COLOR_TEXT};
    }}
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
    QFrame {{
        background-color: {COLOR_CARD_BG};
        border: 1px solid {COLOR_CARD_BORDER};
        border-radius: 6px;
    }}
    QStatusBar {{
        background-color: {COLOR_HEADER_BG};
        color: {COLOR_TEXT_MUTED};
        border-top: 1px solid {COLOR_CARD_BORDER};
        padding: 4px 8px;
    }}
    """
