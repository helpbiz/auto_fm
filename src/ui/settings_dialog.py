# src/ui/settings_dialog.py
"""
config.json 편집 다이얼로그: 근무/상여 기준, 보험 요율, 간접비, 기술자 노임단가.
"""
from decimal import Decimal

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)
from PyQt6.QtCore import Qt

from src.domain.settings_manager import (
    get_default_config,
    get_full_config,
    save,
    INSURANCE_RATE_KEYS,
)
from src.domain.constants.job_data import get_job_mapping_from_file


# 보험 요율 표시명
INSURANCE_LABELS = {
    "industrial_accident": "산재보험 (%)",
    "national_pension": "국민연금 (%)",
    "employment_insurance": "고용보험 (%)",
    "health_insurance": "건강보험 (%)",
    "long_term_care": "노인장기요양 (%)",
    "wage_bond": "임금채권보장 (%)",
    "asbestos_relief": "석면피해구제 (%)",
}


def _rate_to_pct(rate: float) -> str:
    return str(round(rate * 100, 4))


def _pct_to_rate(s: str) -> float:
    try:
        return float(s.strip().replace(",", ".")) / 100.0
    except (ValueError, TypeError):
        return 0.0


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("설정")
        self.setMinimumWidth(480)
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()

        # 탭 1: 근무/상여 기준
        labor_widget = QWidget()
        labor_layout = QFormLayout(labor_widget)
        self.standard_monthly_hours = QLineEdit()
        self.standard_monthly_hours.setPlaceholderText("209")
        labor_layout.addRow("통상 월 근로시간 (시간)", self.standard_monthly_hours)
        self.bonus_annual_rate = QLineEdit()
        self.bonus_annual_rate.setPlaceholderText("4.0")
        labor_layout.addRow("상여금 연율 (예: 400% → 4.0)", self.bonus_annual_rate)
        self.months_per_year = QLineEdit()
        self.months_per_year.setPlaceholderText("12")
        labor_layout.addRow("연간 개월 수", self.months_per_year)
        self.tabs.addTab(labor_widget, "근무/상여")

        # 탭 2: 보험 요율
        insurance_widget = QWidget()
        insurance_layout = QFormLayout(insurance_widget)
        self.insurance_edits = {}
        for key in INSURANCE_RATE_KEYS:
            ed = QLineEdit()
            label = INSURANCE_LABELS.get(key, key)
            insurance_layout.addRow(label, ed)
            self.insurance_edits[key] = ed
        self.tabs.addTab(insurance_widget, "보험 요율")

        # 탭 3: 안전관리비
        safety_widget = QWidget()
        safety_layout = QFormLayout(safety_widget)
        self.safety_management_rate = QLineEdit()
        self.safety_management_rate.setPlaceholderText("1.86")
        safety_layout.addRow("안전관리비 지급요율 (%)", self.safety_management_rate)
        safety_layout.addRow(
            QLabel(""),
            QLabel("직접노무비 합계 × 지급요율 = 안전관리비 (설정에서 요율 변경 시 다음 집계부터 반영)"),
        )
        self.tabs.addTab(safety_widget, "안전관리비")

        # 탭 4: 간접비
        indirect_widget = QWidget()
        indirect_layout = QFormLayout(indirect_widget)
        self.general_admin_max = QLineEdit()
        self.general_admin_max.setPlaceholderText("0.10")
        indirect_layout.addRow("일반관리비 상한 (비율, 예: 10% → 0.10)", self.general_admin_max)
        self.profit_max = QLineEdit()
        self.profit_max.setPlaceholderText("0.10")
        indirect_layout.addRow("이윤 상한 (비율, 예: 10% → 0.10)", self.profit_max)
        self.tabs.addTab(indirect_widget, "간접비")

        # 탭 5: 기술자 노임단가 (직무코드 → 직무 → 일급)
        tech_widget = QWidget()
        tech_layout = QVBoxLayout(tech_widget)
        tech_layout.addWidget(QLabel("직무코드별 기본 일급(원). 비어 있으면 시나리오별 DB 값을 사용합니다."))
        self.tech_table = QTableWidget(0, 3)
        self.tech_table.setHorizontalHeaderLabels(["직무코드", "직무", "일급(원)"])
        self.tech_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tech_table.itemChanged.connect(self._on_tech_item_changed)
        tech_layout.addWidget(self.tech_table)
        add_btn = QPushButton("행 추가")
        add_btn.clicked.connect(self._add_tech_row)
        tech_layout.addWidget(add_btn)
        self.tabs.addTab(tech_widget, "기술자 노임단가")

        layout.addWidget(self.tabs)

        # 저장 / 취소
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_btn = QPushButton("저장")
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton("취소")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        self._load()

    def _load(self):
        config = get_full_config()
        labor = config.get("labor", {})
        self.standard_monthly_hours.setText(str(labor.get("standard_monthly_hours", 209)))
        self.bonus_annual_rate.setText(str(labor.get("bonus_annual_rate", 4.0)))
        self.months_per_year.setText(str(labor.get("months_per_year", 12)))

        rates = config.get("insurance_rates", {})
        for key, ed in self.insurance_edits.items():
            v = rates.get(key)
            ed.setText(_rate_to_pct(v) if v is not None else "")

        safety = config.get("safety", {}) or {}
        self.safety_management_rate.setText(
            _rate_to_pct(safety.get("safety_management_rate", 0.0186))
        )

        indirect = config.get("indirect", {})
        self.general_admin_max.setText(str(indirect.get("general_admin_max", 0.10)))
        self.profit_max.setText(str(indirect.get("profit_max", 0.10)))

        tech = config.get("technician_daily_rates", {}) or {}
        job_mapping = get_job_mapping_from_file()
        # 저장된 단가가 없으면 job_mapping 전체로 테이블 채움 (직무코드·직무 컬럼 채움)
        if not tech and job_mapping:
            tech = {code: 0 for code in sorted(job_mapping.keys())}
        self.tech_table.setRowCount(len(tech))
        for row, (code, wage) in enumerate(tech.items()):
            # 직무코드
            code_item = QTableWidgetItem(str(code))
            self.tech_table.setItem(row, 0, code_item)

            # 직무 컬럼: 직무코드 → 직무명(title) + 직종(grade) 매핑 표시
            meta = job_mapping.get(code) or {}
            if isinstance(meta, dict):
                title = (meta.get("title") or "").strip()
                grade = (meta.get("grade") or "").strip()
                if title and grade:
                    job_display = f"{title} ({grade})"
                elif title:
                    job_display = title
                elif grade:
                    job_display = grade
                else:
                    job_display = code or "-"
            else:
                job_display = str(meta) if meta else (code or "-")
            name_item = QTableWidgetItem(job_display)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.tech_table.setItem(row, 1, name_item)

            # 일급
            wage_item = QTableWidgetItem(f"{int(wage):,}")
            wage_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.tech_table.setItem(row, 2, wage_item)

    def _on_tech_item_changed(self, item):
        """직무코드 변경 시 직무 컬럼에 직무명·직종 매핑 자동 반영"""
        if item.column() == 0:  # 직무코드 컬럼
            row = item.row()
            code = (item.text() or "").strip()
            name_item = self.tech_table.item(row, 1)
            if not name_item:
                return
            if code:
                job_mapping = get_job_mapping_from_file()
                meta = job_mapping.get(code) or {}
                if isinstance(meta, dict):
                    title = (meta.get("title") or "").strip()
                    grade = (meta.get("grade") or "").strip()
                    if title and grade:
                        job_display = f"{title} ({grade})"
                    elif title:
                        job_display = title
                    elif grade:
                        job_display = grade
                    else:
                        job_display = code
                else:
                    job_display = str(meta) if meta else code
            else:
                job_display = ""
            self.tech_table.blockSignals(True)
            try:
                name_item.setText(job_display)
            finally:
                self.tech_table.blockSignals(False)

    def _add_tech_row(self):
        r = self.tech_table.rowCount()
        self.tech_table.insertRow(r)
        # 직무코드
        self.tech_table.setItem(r, 0, QTableWidgetItem(""))
        # 직무명 (읽기전용, 비어있음)
        name_item = QTableWidgetItem("")
        name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        self.tech_table.setItem(r, 1, name_item)
        # 일급
        wage_item = QTableWidgetItem("0")
        wage_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        self.tech_table.setItem(r, 2, wage_item)

    def _collect_tech_rates(self) -> dict:
        out = {}
        for row in range(self.tech_table.rowCount()):
            code_item = self.tech_table.item(row, 0)
            wage_item = self.tech_table.item(row, 2)  # 일급은 이제 컬럼 2
            code = (code_item.text() or "").strip()
            if not code:
                continue
            try:
                wage = int((wage_item.text() or "0").strip().replace(",", ""))
            except ValueError:
                wage = 0
            out[code] = wage
        return out

    def _save(self):
        try:
            labor = {
                "standard_monthly_hours": int(self.standard_monthly_hours.text() or "209"),
                "bonus_annual_rate": float(self.bonus_annual_rate.text() or "4.0"),
                "months_per_year": int(self.months_per_year.text() or "12"),
            }
        except ValueError as e:
            QMessageBox.warning(self, "입력 오류", f"근무/상여 값이 올바르지 않습니다.\n{e}")
            return

        insurance_rates = {}
        for key, ed in self.insurance_edits.items():
            t = ed.text()
            if t:
                insurance_rates[key] = _pct_to_rate(t)
            else:
                insurance_rates[key] = get_default_config()["insurance_rates"][key]

        try:
            indirect = {
                "general_admin_max": float(self.general_admin_max.text() or "0.10"),
                "profit_max": float(self.profit_max.text() or "0.10"),
            }
        except ValueError as e:
            QMessageBox.warning(self, "입력 오류", f"간접비 값이 올바르지 않습니다.\n{e}")
            return

        safety_rate_str = (self.safety_management_rate.text() or "").strip()
        safety_management_rate = _pct_to_rate(safety_rate_str) if safety_rate_str else 0.0186
        safety_cfg = {"safety_management_rate": safety_management_rate}

        tech = self._collect_tech_rates()

        config = {
            "labor": labor,
            "insurance_rates": insurance_rates,
            "safety": safety_cfg,
            "indirect": indirect,
            "technician_daily_rates": tech,
        }
        save(config)
        QMessageBox.information(self, "설정", "설정이 저장되었습니다. 적용된 값은 다음 계산부터 반영됩니다.")
        self.accept()
