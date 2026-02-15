"""휴일근무일수 계산 탭: 용역기간현황표 형식(평일·토·일·공휴일·소계·계) 및 참고 휴일근로시간."""
import calendar
from datetime import date

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QSpinBox,
    QHBoxLayout,
    QFormLayout,
    QDoubleSpinBox,
    QAbstractItemView,
    QComboBox,
)
from PyQt6.QtCore import Qt

from .theme import SECTION_TITLE_STYLE, CARD_STYLE, COLOR_HEADER_BG

# 테이블 행 인덱스
ROW_WEEKDAYS = 0      # 평일
ROW_SATURDAY = 1      # 토요일
ROW_SUNDAY = 2        # 일요일
ROW_PUBLIC_HOLIDAY = 3  # 공휴일 및 명절 (편집)
ROW_SUBTOTAL = 4      # 소계 (토+공휴)
ROW_TOTAL = 5         # 계
COL_LABEL = 0
COL_JAN = 1
COL_DEC = 12
COL_SUM = 13   # 계(연간)
COL_REMARK = 14  # 비고

# 연도별 법정공휴일·명절 월별 일수 (1월~12월). 해당 연도 선택 시 공휴일 행이 모두 0이면 이 값으로 채움.
DEFAULT_PUBLIC_HOLIDAYS_BY_YEAR: dict[int, list[int]] = {
    2024: [1, 4, 1, 0, 2, 1, 0, 1, 3, 2, 0, 1],  # 신정, 설(4), 삼일절, 어린이날+대체, 현충일, 광복절, 추석(3), 개천절·한글날, 크리스마스
    2025: [1, 3, 1, 0, 2, 1, 0, 1, 3, 2, 0, 1],  # 2025년 참고 (설 3일 등)
}


def _count_weekdays_sat_sun(year: int, month: int) -> tuple[int, int, int]:
    """해당 연·월의 평일(월~금), 토요일, 일요일 수를 반환. (calendar: 0=월, 6=일)"""
    weekdays = 0
    sat = 0
    sun = 0
    for day in range(1, calendar.monthrange(year, month)[1] + 1):
        wd = date(year, month, day).weekday()  # 0=Mon .. 6=Sun
        if wd < 5:
            weekdays += 1
        elif wd == 5:
            sat += 1
        else:
            sun += 1
    return weekdays, sat, sun


class HolidayWorkDaysPanel(QWidget):
    """용역기간현황표 형식 테이블 + 연간 휴일근무 일수 입력 및 참고 휴일근로시간."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        title = QLabel("휴일근무일수 계산 (용역기간현황표)")
        title.setStyleSheet(SECTION_TITLE_STYLE)
        layout.addWidget(title)

        # 연도 선택
        year_row = QHBoxLayout()
        year_row.addWidget(QLabel("기간:"))
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2020, 2040)
        self.year_spin.setValue(date.today().year)
        self.year_spin.setToolTip("용역기간 연도")
        year_row.addWidget(self.year_spin)
        self.period_label = QLabel("")
        year_row.addWidget(self.period_label)
        year_row.addStretch()
        layout.addLayout(year_row)

        # 용역기간현황표 테이블
        self.table = QTableWidget(6, 15)
        self.table.setHorizontalHeaderLabels([
            "구분", "1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월", "계", "비고"
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setMinimumSectionSize(36)
        self.table.setStyleSheet(f"""
            QTableWidget {{ gridline-color: #e0e0e0; }}
            QHeaderView::section {{ background-color: {COLOR_HEADER_BG}; padding: 4px; }}
        """)
        layout.addWidget(self.table)

        # 행 라벨 및 편집/계산 설정
        row_labels = ["평일", "토요일", "일요일", "공휴일 및 명절", "소계", "계"]
        for r, label in enumerate(row_labels):
            item = QTableWidgetItem(label)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(r, COL_LABEL, item)

        # 공휴일 행: 1~12월 셀에 스핀박스 대신 숫자 편집 가능하도록 (간단히 QTableWidgetItem + 편집 허용)
        for c in range(COL_JAN, COL_SUM):
            item = QTableWidgetItem("0")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(ROW_PUBLIC_HOLIDAY, c, item)
        self.table.setItem(ROW_PUBLIC_HOLIDAY, COL_SUM, QTableWidgetItem("0"))
        self.table.setItem(ROW_PUBLIC_HOLIDAY, COL_REMARK, QTableWidgetItem(""))

        # 비고 열: 소계 행에 "토+공휴"
        self.table.setItem(ROW_SUBTOTAL, COL_REMARK, QTableWidgetItem("토+공휴"))
        for c in range(COL_LABEL, COL_REMARK):
            if self.table.item(ROW_SUBTOTAL, c) is None:
                self.table.setItem(ROW_SUBTOTAL, c, QTableWidgetItem(""))

        # 소계·계 행 셀 읽기 전용
        for r in (ROW_WEEKDAYS, ROW_SATURDAY, ROW_SUNDAY, ROW_SUBTOTAL, ROW_TOTAL):
            for c in range(COL_JAN, COL_REMARK + 1):
                if self.table.item(r, c) is None:
                    self.table.setItem(r, c, QTableWidgetItem(""))
                if r != ROW_PUBLIC_HOLIDAY:
                    self.table.item(r, c).setFlags(
                        self.table.item(r, c).flags() & ~Qt.ItemFlag.ItemIsEditable
                    )

        # 공휴일 행: 1~12월만 편집 가능, 계·비고는 읽기 전용
        for c in range(COL_JAN, COL_SUM):
            self.table.item(ROW_PUBLIC_HOLIDAY, c).setFlags(
                Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
            )
        for c in (COL_SUM, COL_REMARK):
            it = self.table.item(ROW_PUBLIC_HOLIDAY, c)
            if it is not None:
                it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)

        # 하단 참고: 연간 휴일근무 가능일수(토+법정+대체), 연간 휴일근무 일수, 월 평균, 참고 휴일근로시간
        result_frame = QFrame()
        result_frame.setStyleSheet(CARD_STYLE)
        result_form = QFormLayout(result_frame)
        # 연간 휴일근무 가능일수 = 토요일 + 주간 법정공휴일 + 주간 대체공휴일
        self.statutory_holidays_spin = QSpinBox()
        self.statutory_holidays_spin.setRange(0, 366)
        self.statutory_holidays_spin.setValue(14)
        self.statutory_holidays_spin.setToolTip("해당 연도 법정공휴일 수")
        result_form.addRow("주간 법정공휴일", self.statutory_holidays_spin)
        self.substitute_holidays_spin = QSpinBox()
        self.substitute_holidays_spin.setRange(0, 366)
        self.substitute_holidays_spin.setValue(0)
        self.substitute_holidays_spin.setToolTip("해당 연도 대체공휴일 수")
        result_form.addRow("주간 대체공휴일", self.substitute_holidays_spin)
        self.label_annual_holidays = QLabel("—")
        self.label_annual_holidays.setToolTip("토요일(연간) + 주간 법정공휴일 + 주간 대체공휴일")
        result_form.addRow("연간 휴일근무 가능일수", self.label_annual_holidays)
        self.center_count = QComboBox()
        self.center_count.addItems([str(i) for i in range(1, 11)])
        self.center_count.setToolTip("근무인원을 집하장별로 배치할 집하장 수 (1~10)")
        result_form.addRow("집하장 수", self.center_count)
        self.shift_combo = QComboBox()
        self.shift_combo.addItems(["미운영", "2교대", "3교대"])
        self.shift_combo.setToolTip("선택 시 관리소장 제외 인원 또는 집하장·인원운영으로 월 평균 휴일근무일수 자동 산정")
        result_form.addRow("휴일교대근무제", self.shift_combo)
        self.crew_combo_3 = QComboBox()
        self.crew_combo_3.addItems(["1인 1조", "2인 1조", "3인 1조"])
        self.crew_combo_3.setToolTip("3교대 선택 시: 집하장별 3교대 조당 인원. 필요인원 = 집하장 수 × 3 × 조당 인원")
        result_form.addRow("인원운영(3교대)", self.crew_combo_3)
        self.headcount_excl_manager = QSpinBox()
        self.headcount_excl_manager.setRange(0, 9999)
        self.headcount_excl_manager.setValue(0)
        self.headcount_excl_manager.setSpecialValueText("자동")
        self.headcount_excl_manager.setToolTip("관리소장 제외 인원. 0이면 직무별 인원입력에서 자동 반영.")
        result_form.addRow("관리소장 제외 인원", self.headcount_excl_manager)
        self.annual_holiday_work_days = QDoubleSpinBox()
        self.annual_holiday_work_days.setRange(0, 366)
        self.annual_holiday_work_days.setDecimals(1)
        self.annual_holiday_work_days.setValue(0)
        self.annual_holiday_work_days.setToolTip("휴일교대근무제 미운영 시 직접 입력. 2/3교대 시 참고용.")
        result_form.addRow("연간 휴일근무 일수", self.annual_holiday_work_days)
        self.label_monthly_holiday_work = QLabel("—")
        self.label_monthly_holiday_work.setToolTip("2/3교대 시: 가능일수÷(교대수×인원)×교대수÷12 또는 가능일수÷인원÷12")
        result_form.addRow("월 평균 휴일근무일수", self.label_monthly_holiday_work)
        self.label_holiday_hours_ref = QLabel("—")
        self.label_holiday_hours_ref.setToolTip("직무별 인원입력 탭 '휴일근로일수' 참고 (일×8 = 시간/월)")
        result_form.addRow("참고 휴일근로시간(시간/월)", self.label_holiday_hours_ref)
        layout.addWidget(result_frame)
        layout.addStretch()

        self.year_spin.valueChanged.connect(self._refresh_table)
        self.table.itemChanged.connect(self._on_cell_changed)
        self.statutory_holidays_spin.valueChanged.connect(self._update_ref_result)
        self.substitute_holidays_spin.valueChanged.connect(self._update_ref_result)
        self.center_count.currentTextChanged.connect(self._update_ref_result)
        self.shift_combo.currentTextChanged.connect(self._on_shift_changed)
        self.crew_combo_3.currentTextChanged.connect(self._update_ref_result)
        self.headcount_excl_manager.valueChanged.connect(self._update_ref_result)
        self.annual_holiday_work_days.valueChanged.connect(self._update_ref_result)
        self._refresh_table()
        self._on_shift_changed()
        self._update_ref_result()

    def _on_shift_changed(self) -> None:
        is_3shift = self.shift_combo.currentText() == "3교대"
        self.crew_combo_3.setEnabled(is_3shift)
        self._update_ref_result()

    def _on_cell_changed(self, item: QTableWidgetItem) -> None:
        if item.row() == ROW_PUBLIC_HOLIDAY and COL_JAN <= item.column() < COL_SUM:
            self._refresh_subtotal_and_total()
            self._update_ref_result()

    def _refresh_table(self) -> None:
        year = self.year_spin.value()
        self.period_label.setText(f"{year}년 1월 1일 ~ {year}년 12월 31일 (12개월)")

        # 기존 공휴일 입력값 유지 (연도만 바꿀 때). 전부 0이면 해당 연도 기본값(법정공휴일·명절) 사용
        saved_holidays = []
        for c in range(COL_JAN, COL_SUM):
            it = self.table.item(ROW_PUBLIC_HOLIDAY, c)
            if it and it.text().strip() != "":
                try:
                    saved_holidays.append(int(float(it.text())))
                except ValueError:
                    saved_holidays.append(0)
            else:
                saved_holidays.append(0)
        if len(saved_holidays) < 12:
            saved_holidays.extend([0] * (12 - len(saved_holidays)))
        if all(x == 0 for x in saved_holidays) and year in DEFAULT_PUBLIC_HOLIDAYS_BY_YEAR:
            saved_holidays = list(DEFAULT_PUBLIC_HOLIDAYS_BY_YEAR[year])

        # 평일·토·일·공휴일 계산 (평일 = 당월 일수 - 토 - 일 - 공휴일, 합계가 365/366일을 넘지 않도록)
        self.table.blockSignals(True)
        try:
            for month in range(1, 13):
                c = month  # 1월=COL_JAN, ...
                days_in_month = calendar.monthrange(year, month)[1]
                _, sat, sun = _count_weekdays_sat_sun(year, month)
                pub = saved_holidays[c - 1]
                # 평일 = 나머지(당월 일수 - 토 - 일 - 공휴일), 0 미만이면 0으로
                wd = max(0, days_in_month - sat - sun - pub)
                self.table.item(ROW_WEEKDAYS, c).setText(str(wd))
                self.table.item(ROW_SATURDAY, c).setText(str(sat))
                self.table.item(ROW_SUNDAY, c).setText(str(sun))
                self.table.item(ROW_PUBLIC_HOLIDAY, c).setText(str(pub))
            self._refresh_subtotal_and_total()
        finally:
            self.table.blockSignals(False)
        self._update_ref_result()

    def _refresh_subtotal_and_total(self) -> None:
        """평일(당월일수-토-일-공휴), 소계(토+공휴), 계(당월 일수) 행 갱신. 연간 합계가 365/366일을 넘지 않도록."""
        year = self.year_spin.value()
        for month in range(1, 13):
            c = month
            days_in_month = calendar.monthrange(year, month)[1]
            _, sat, sun = _count_weekdays_sat_sun(year, month)
            pub = _safe_int(self.table.item(ROW_PUBLIC_HOLIDAY, c))
            wd = max(0, days_in_month - sat - sun - pub)
            self.table.item(ROW_WEEKDAYS, c).setText(str(wd))
            self.table.item(ROW_SUBTOTAL, c).setText(str(sat + pub))
            self.table.item(ROW_TOTAL, c).setText(str(days_in_month))

        # 연간 계 열
        for r in range(6):
            total = 0
            for c in range(COL_JAN, COL_SUM):
                total += _safe_int(self.table.item(r, c))
            self.table.item(r, COL_SUM).setText(str(total))

    def _update_ref_result(self) -> None:
        """연간 휴일근무 가능일수(토+법정+대체), 월 평균 휴일근무일수, 참고 휴일근로시간 갱신."""
        sat_total = _safe_int(self.table.item(ROW_SATURDAY, COL_SUM))
        statutory = self.statutory_holidays_spin.value()
        substitute = self.substitute_holidays_spin.value()
        annual_available = sat_total + statutory + substitute
        self.label_annual_holidays.setText(str(annual_available))
        shift_type = self.shift_combo.currentText()
        n = self.headcount_excl_manager.value()
        centers = max(1, int(self.center_count.currentText()))
        if shift_type == "미운영":
            monthly = self.annual_holiday_work_days.value() / 12
        elif shift_type == "2교대":
            if n > 0:
                monthly = annual_available / n / 12
            else:
                monthly = annual_available / 24
        else:  # 3교대: 집하장 수 × 3교대 × 인원운영(1인 1조/2인 1조/3인 1조)
            crew_text = self.crew_combo_3.currentText()
            crew_size = 1 if "1인" in crew_text else (2 if "2인" in crew_text else 3)
            total_slots = centers * 3 * crew_size
            if total_slots > 0:
                monthly = annual_available / 12 / total_slots
            else:
                monthly = annual_available / 36
        self.label_monthly_holiday_work.setText(f"{monthly:.2f}")
        self.label_holiday_hours_ref.setText(f"{monthly * 8:.2f}")

    def get_values(self) -> dict:
        public_by_month = []
        for c in range(COL_JAN, COL_SUM):
            public_by_month.append(_safe_int(self.table.item(ROW_PUBLIC_HOLIDAY, c)))
        ct = self.crew_combo_3.currentText()
        crew_size = 1 if "1인" in ct else (2 if "2인" in ct else 3)
        return {
            "year": self.year_spin.value(),
            "public_holidays_by_month": public_by_month,
            "statutory_holidays": self.statutory_holidays_spin.value(),
            "substitute_holidays": self.substitute_holidays_spin.value(),
            "center_count": int(self.center_count.currentText()),
            "shift_type": self.shift_combo.currentText(),
            "crew_size_3shift": crew_size,
            "headcount_excl_manager": self.headcount_excl_manager.value(),
            "monthly_work_days": self._computed_monthly_work_days(),
            "annual_holiday_work_days": self.annual_holiday_work_days.value(),
        }

    def _computed_monthly_work_days(self) -> float:
        """연간 평일 합계 / 12 (참고용 월 평균 근무일수)."""
        total_weekdays = _safe_int(self.table.item(ROW_WEEKDAYS, COL_SUM))
        return round(total_weekdays / 12, 1) if total_weekdays else 20.6

    def set_values(self, values: dict) -> None:
        if values.get("year") is not None:
            self.year_spin.setValue(int(values["year"]))
        if "public_holidays_by_month" in values and isinstance(values.get("public_holidays_by_month"), list):
            arr = values["public_holidays_by_month"]
            for c in range(COL_JAN, COL_SUM):
                idx = c - COL_JAN
                val = int(arr[idx]) if idx < len(arr) else 0
                self.table.item(ROW_PUBLIC_HOLIDAY, c).setText(str(val))
        if values.get("statutory_holidays") is not None:
            self.statutory_holidays_spin.setValue(int(values["statutory_holidays"]))
        if values.get("substitute_holidays") is not None:
            self.substitute_holidays_spin.setValue(int(values["substitute_holidays"]))
        if values.get("center_count") is not None:
            v = max(1, min(10, int(values["center_count"])))
            idx = self.center_count.findText(str(v))
            if idx >= 0:
                self.center_count.setCurrentIndex(idx)
        if values.get("shift_type") in ("미운영", "2교대", "3교대"):
            idx = self.shift_combo.findText(values["shift_type"])
            if idx >= 0:
                self.shift_combo.setCurrentIndex(idx)
        if values.get("crew_size_3shift") in (1, 2, 3):
            idx = int(values["crew_size_3shift"]) - 1
            self.crew_combo_3.setCurrentIndex(min(idx, 2))
        if values.get("headcount_excl_manager") is not None:
            self.headcount_excl_manager.setValue(int(values["headcount_excl_manager"]))
        # 연도/공휴일 반영 후 평일·토·일·소계·계 재계산
        self._refresh_table()
        if "annual_holiday_work_days" in values:
            self.annual_holiday_work_days.setValue(float(values["annual_holiday_work_days"]))
        self._update_ref_result()

    def on_change(self, callback) -> None:
        self.year_spin.valueChanged.connect(lambda _: callback())
        self.table.itemChanged.connect(lambda _: callback())
        self.statutory_holidays_spin.valueChanged.connect(lambda _: callback())
        self.substitute_holidays_spin.valueChanged.connect(lambda _: callback())
        self.center_count.currentTextChanged.connect(lambda _: callback())
        self.shift_combo.currentTextChanged.connect(lambda _: callback())
        self.crew_combo_3.currentTextChanged.connect(lambda _: callback())
        self.headcount_excl_manager.valueChanged.connect(lambda _: callback())
        self.annual_holiday_work_days.valueChanged.connect(lambda _: callback())

    def set_headcount_excluding_manager(self, count: int) -> None:
        """직무별 인원입력에서 관리소장 제외 인원으로 자동 반영 (0이면 자동 미반영)."""
        self.headcount_excl_manager.setValue(max(0, count))


def _safe_int(item: QTableWidgetItem | None) -> int:
    if item is None or not item.text().strip():
        return 0
    try:
        return int(float(item.text()))
    except (ValueError, TypeError):
        return 0
