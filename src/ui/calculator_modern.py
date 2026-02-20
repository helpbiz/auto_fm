# src/ui/calculator_modern.py
"""
인건비·보험 요율 실시간 미리보기용 Modern UI (CustomTkinter).
LaborCostCalculator 엔진 기반, 사용자가 인건비와 보험 요율을 수정하면 즉시 결과 반영.
"""
from decimal import Decimal
from typing import Any, Callable, Dict, Optional

try:
    import customtkinter as ctk
except ImportError:
    ctk = None  # type: ignore

from src.domain.context.calc_context import CalcContext
from src.domain.calculator.labor import LaborCostCalculator
from src.domain.wage_manager import WageManager


# 기본 근무/수당 상수 (월 환산)
DEFAULT_MONTHLY_WORKDAYS = Decimal("20.6")
DEFAULT_DAILY_HOURS = Decimal("8")
DEFAULT_WEEKLY_HOLIDAY_DAYS = Decimal("52") / Decimal("12")
DEFAULT_ANNUAL_LEAVE_DAYS = Decimal("15") / Decimal("12")

# 보험 요율 기본값 (클래스와 동일, 비율 소수)
RATE_LABELS = [
    ("industrial_accident", "산재보험 (%)", Decimal("0.009")),
    ("national_pension", "국민연금 (%)", Decimal("0.045")),
    ("employment_insurance", "고용보험 (%)", Decimal("0.0115")),
    ("health_insurance", "건강보험 (%)", Decimal("0.03545")),
    ("long_term_care", "노인장기요양 (%)", Decimal("0.1281")),
    ("wage_bond", "임금채권보장 (%)", Decimal("0.0006")),
    ("asbestos_relief", "석면피해구제 (%)", Decimal("0.00004")),
]


def _to_decimal(s: str, default: Decimal = Decimal("0")) -> Decimal:
    s = (s or "").strip().replace(",", "")
    if not s:
        return default
    try:
        return Decimal(s)
    except Exception:
        return default


def _rate_to_percent(rate: Decimal) -> str:
    return str(round(float(rate * Decimal("100")), 3))


def _percent_to_rate(percent_str: str) -> Optional[Decimal]:
    v = _to_decimal(percent_str, default=Decimal("-1"))
    if v < 0:
        return None
    return v / Decimal("100")


def _format_money(n: int) -> str:
    return f"{n:,}"


def _build_context(
    daily_wage: str,
    headcount: str,
    monthly_workdays: str,
    daily_hours: str,
    weekly_holiday: str,
    annual_leave: str,
    rate_values: Dict[str, str],
) -> Optional[CalcContext]:
    wage = _to_decimal(daily_wage)
    cnt = _to_decimal(headcount, default=Decimal("1"))
    if cnt <= 0:
        cnt = Decimal("1")
    mdays = _to_decimal(monthly_workdays, default=DEFAULT_MONTHLY_WORKDAYS)
    dhours = _to_decimal(daily_hours, default=DEFAULT_DAILY_HOURS)
    wdays = _to_decimal(weekly_holiday, default=DEFAULT_WEEKLY_HOLIDAY_DAYS)
    adays = _to_decimal(annual_leave, default=DEFAULT_ANNUAL_LEAVE_DAYS)

    manpower = {"default": cnt}
    wage_rate = {"default": wage}
    expenses: Dict[str, Decimal] = {}

    ctx = CalcContext(
        project_name="미리보기",
        year=2025,
        monthly_workdays=mdays,
        daily_work_hours=dhours,
        manpower=manpower,
        wage_rate=wage_rate,
        weekly_holiday_days=wdays,
        annual_leave_days=adays,
        expenses=expenses,
    )

    # 보험 요율 오버라이드 (퍼센트 문자열 -> Decimal)
    for key, _label, _ in RATE_LABELS:
        r = _percent_to_rate(rate_values.get(key, ""))
        if r is not None:
            setattr(ctx, f"{key}_rate", r)
    return ctx


def _run_calc(ctx: CalcContext) -> Dict[str, Any]:
    calc = LaborCostCalculator(ctx)
    return calc.calculate()


class CalculatorModernUI:
    """CustomTkinter 기반 인건비·보험요율 실시간 계산기 창. 연도/직무코드 변경 시 WageManager(wages_[year].json) 단가로 자동 갱신."""

    def __init__(self) -> None:
        if ctk is None:
            raise RuntimeError("customtkinter가 필요합니다. pip install customtkinter")
        self.root = ctk.CTk()
        self.root.title("인건비 계산기 · 실시간 미리보기")
        self.root.geometry("920x680")
        self.root.minsize(800, 560)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self._wage_manager = WageManager()
        years = self._wage_manager.list_available_years()
        self._wage_year = int(years[0]) if years else 2025

        self._rate_entries: Dict[str, ctk.CTkEntry] = {}
        self._build_ui()
        self._refresh()

    def _build_ui(self) -> None:
        main = ctk.CTkFrame(self.root, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=16, pady=16)

        # 상단: 인건비 입력
        left = ctk.CTkFrame(main, corner_radius=12, fg_color=("#e0e0e0", "#2b2b2b"))
        left.pack(side="left", fill="both", expand=False, padx=(0, 8), pady=0)
        left.configure(width=320)

        title_left = ctk.CTkLabel(left, text="인건비 입력", font=ctk.CTkFont(size=16, weight="bold"))
        title_left.pack(pady=(16, 12), padx=16, anchor="w")

        # 연도 선택 (변경 시 해당 연도 단가로 즉시 재계산)
        ctk.CTkLabel(left, text="연도", font=ctk.CTkFont(size=12, weight="bold")).pack(
            pady=(0, 2), padx=16, anchor="w"
        )
        year_values = [str(y) for y in self._wage_manager.list_available_years()]
        if not year_values:
            year_values = [str(self._wage_year)]
        self._year_combo = ctk.CTkComboBox(
            left, values=year_values, width=200, command=self._on_year_changed
        )
        self._year_combo.pack(pady=4, padx=16, anchor="w")
        if str(self._wage_year) in year_values:
            self._year_combo.set(str(self._wage_year))

        # 직무코드 (입력 시 해당 연도 단가 자동 적용 → 테이블 갱신)
        ctk.CTkLabel(left, text="직무코드 (선택)", font=ctk.CTkFont(size=12, weight="bold")).pack(
            pady=(8, 2), padx=16, anchor="w"
        )
        self._job_code_entry = ctk.CTkEntry(
            left, placeholder_text="예: M101, E501", width=200
        )
        self._job_code_entry.pack(pady=4, padx=16, anchor="w")
        self._job_code_entry.bind("<KeyRelease>", lambda e: self._on_job_code_changed())

        # 일급 (직무코드 미입력 시 수동 입력)
        ctk.CTkLabel(left, text="일급 (원) — 직무코드 없을 때", font=ctk.CTkFont(size=12, weight="bold")).pack(
            pady=(8, 2), padx=16, anchor="w"
        )
        self._daily_wage = ctk.CTkEntry(left, placeholder_text="일급 (원)", width=200)
        self._daily_wage.pack(pady=4, padx=16, anchor="w")
        self._daily_wage.bind("<KeyRelease>", lambda e: self._refresh())

        self._headcount = ctk.CTkEntry(left, placeholder_text="인원 수", width=200)
        self._headcount.insert(0, "1")
        self._headcount.pack(pady=6, padx=16, anchor="w")
        self._headcount.bind("<KeyRelease>", lambda e: self._refresh())

        ctk.CTkLabel(left, text="근무 기준 (월)", font=ctk.CTkFont(size=12, weight="bold")).pack(
            pady=(14, 4), padx=16, anchor="w"
        )
        self._monthly_workdays = ctk.CTkEntry(left, placeholder_text="월 근무일수 (예: 20.6)", width=200)
        self._monthly_workdays.insert(0, "20.6")
        self._monthly_workdays.pack(pady=4, padx=16, anchor="w")
        self._monthly_workdays.bind("<KeyRelease>", lambda e: self._refresh())

        self._daily_hours = ctk.CTkEntry(left, placeholder_text="일 근무시간 (예: 8)", width=200)
        self._daily_hours.insert(0, "8")
        self._daily_hours.pack(pady=4, padx=16, anchor="w")
        self._daily_hours.bind("<KeyRelease>", lambda e: self._refresh())

        self._weekly_holiday = ctk.CTkEntry(left, placeholder_text="주휴일수 월환산 (예: 4.33)", width=200)
        self._weekly_holiday.insert(0, "4.33")
        self._weekly_holiday.pack(pady=4, padx=16, anchor="w")
        self._weekly_holiday.bind("<KeyRelease>", lambda e: self._refresh())

        self._annual_leave = ctk.CTkEntry(left, placeholder_text="연차일수 월환산 (예: 1.25)", width=200)
        self._annual_leave.insert(0, "1.25")
        self._annual_leave.pack(pady=4, padx=16, anchor="w")
        self._annual_leave.bind("<KeyRelease>", lambda e: self._refresh())

        # 보험 요율
        rate_frame = ctk.CTkFrame(main, corner_radius=12, fg_color=("#e8e8e8", "#333333"))
        rate_frame.pack(side="left", fill="y", expand=False, padx=8, pady=0)
        rate_frame.configure(width=260)

        ctk.CTkLabel(rate_frame, text="보험 요율 (%)", font=ctk.CTkFont(size=16, weight="bold")).pack(
            pady=(16, 12), padx=16, anchor="w"
        )
        for key, label, default_pct in RATE_LABELS:
            row = ctk.CTkFrame(rate_frame, fg_color="transparent")
            row.pack(fill="x", pady=4, padx=16)
            ctk.CTkLabel(row, text=label, width=140, anchor="w").pack(side="left", padx=(0, 8))
            ent = ctk.CTkEntry(row, width=80)
            ent.insert(0, _rate_to_percent(default_pct))
            ent.pack(side="right")
            ent.bind("<KeyRelease>", lambda e, k=key: self._refresh())
            self._rate_entries[key] = ent

        # 결과 패널
        right = ctk.CTkFrame(main, corner_radius=12, fg_color=("#d8d8d8", "#1e1e1e"))
        right.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=0)

        ctk.CTkLabel(right, text="계산 결과 (실시간)", font=ctk.CTkFont(size=16, weight="bold")).pack(
            pady=(16, 8), padx=16, anchor="w"
        )
        self._result_text = ctk.CTkTextbox(right, font=ctk.CTkFont(family="Consolas", size=13))
        self._result_text.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    def _get_rate_values(self) -> Dict[str, str]:
        return {k: (v.get() or "").strip() for k, v in self._rate_entries.items()}

    def _on_year_changed(self, choice: str) -> None:
        """연도 변경 시 단가 연도 갱신 후 전체 테이블(결과) 즉시 재계산."""
        try:
            self._wage_year = int(choice)
        except (TypeError, ValueError):
            pass
        self._refresh()

    def _on_job_code_changed(self) -> None:
        """직무코드 입력/변경 시 해당 연도 단가로 즉시 재계산."""
        self._refresh()

    def _get_effective_daily_wage(self) -> str:
        """직무코드+연도로 WageManager(wages_[year].json)에서 단가 조회, 없으면 일급 입력란 값 사용."""
        job_code = (self._job_code_entry.get() or "").strip()
        if job_code:
            w = self._wage_manager.get_wage(job_code, self._wage_year)
            if w is not None and w > 0:
                return str(w)
        return self._daily_wage.get() or ""

    def _refresh(self) -> None:
        daily_wage_str = self._get_effective_daily_wage()
        ctx = _build_context(
            daily_wage_str,
            self._headcount.get() or "",
            self._monthly_workdays.get() or "",
            self._daily_hours.get() or "",
            self._weekly_holiday.get() or "",
            self._annual_leave.get() or "",
            self._get_rate_values(),
        )
        if ctx is None:
            self._result_text.delete("1.0", "end")
            self._result_text.insert("1.0", "입력값을 확인해 주세요.")
            return
        try:
            res = _run_calc(ctx)
        except Exception as e:
            self._result_text.delete("1.0", "end")
            self._result_text.insert("1.0", f"계산 오류:\n{e}")
            return
        lines = [
            "━━━ 급여 ━━━",
            f"  기본급(월)        {_format_money(res['base_salary'])} 원",
            f"  주휴수당          {_format_money(res['weekly_holiday_pay'])} 원",
            f"  제수당 합계       {_format_money(res['allowance'])} 원",
            f"    · 연차수당      {_format_money(res['annual_leave_allowance'])} 원",
            f"  상여금(월)        {_format_money(res['bonus'])} 원",
            f"  퇴직급여충당금    {_format_money(res['retirement'])} 원",
            "",
            "  ▶ 인건비 소계     " + _format_money(res["labor_subtotal"]) + " 원",
            "",
            "━━━ 보험료 ━━━",
            f"  산재보험          {_format_money(res['industrial_accident'])} 원",
            f"  국민연금          {_format_money(res['national_pension'])} 원",
            f"  고용보험          {_format_money(res['employment_insurance'])} 원",
            f"  건강보험          {_format_money(res['health_insurance'])} 원",
            f"  노인장기요양      {_format_money(res['long_term_care'])} 원",
            f"  임금채권보장      {_format_money(res['wage_bond'])} 원",
            f"  석면피해구제      {_format_money(res['asbestos_relief'])} 원",
            "",
            "  ▶ 보험료 합계     " + _format_money(res["insurance_total"]) + " 원",
            "",
            "━━━━━━━━━━━━━━━━━━",
            "  ★ 총 인건비       " + _format_money(res["total_labor_cost"]) + " 원",
        ]
        self._result_text.delete("1.0", "end")
        self._result_text.insert("1.0", "\n".join(lines))

    def run(self) -> None:
        self.root.mainloop()


def main_calculator_ui() -> None:
    """실시간 인건비 계산기 UI 진입점."""
    if ctk is None:
        raise RuntimeError("customtkinter가 필요합니다. pip install customtkinter")
    app = CalculatorModernUI()
    app.run()


if __name__ == "__main__":
    main_calculator_ui()
