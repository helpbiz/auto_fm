"""
비용 비중 도넛 차트 (인건비, 경비, 일반관리비, 이윤).
캔버스 전체 clear 없이 wedge 각도·범례만 갱신하여 깜빡임을 줄임.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt

from .theme import SECTION_TITLE_STYLE, COLOR_TABLE_ALT

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib
    matplotlib.use("QtAgg")
    _HAS_MATPLOTLIB = True
except ImportError:
    _HAS_MATPLOTLIB = False


def _aggregator_to_segments(aggregator) -> list[tuple[str, int, str]]:
    """(라벨, 금액, 색상) 리스트. 합이 0이면 비율 대신 균등 표시용 더미."""
    labor = getattr(aggregator, "labor_total", 0) or 0
    fixed = getattr(aggregator, "fixed_expense_total", 0) or 0
    variable = getattr(aggregator, "variable_expense_total", 0) or 0
    passthrough = getattr(aggregator, "passthrough_expense_total", 0) or 0
    overhead = getattr(aggregator, "overhead_cost", 0) or 0
    profit = getattr(aggregator, "profit", 0) or 0

    expense_total = fixed + variable + passthrough
    segments = [
        ("인건비", labor, "#2196F3"),
        ("경비", expense_total, "#4CAF50"),
        ("일반관리비", overhead, "#FF9800"),
        ("이윤", profit, "#9C27B0"),
    ]
    return segments


def _angles_from_sizes(sizes: list[float], start_deg: float = 90.0) -> list[tuple[float, float]]:
    """비율 합=1 기준으로 wedge별 (theta1, theta2) 도 단위. 반시계 방향."""
    total = sum(sizes)
    if total <= 0:
        return []
    cum = 0.0
    out = []
    for s in sizes:
        theta2 = start_deg - 360.0 * cum
        cum += s / total
        theta1 = start_deg - 360.0 * cum
        out.append((theta1, theta2))
    return out


class DonutChartWidget(QWidget):
    """우측 사이드바용 도넛 차트. Aggregator 또는 None(빈 상태) 받음."""

    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        title = QLabel("비용 비중")
        title.setStyleSheet(SECTION_TITLE_STYLE)
        layout.addWidget(title)

        if _HAS_MATPLOTLIB:
            self._fig = Figure(figsize=(2.8, 2.8), facecolor=COLOR_TABLE_ALT)
            self._ax = self._fig.add_subplot(111)
            self._canvas = FigureCanvas(self._fig)
            self._canvas.setMinimumSize(180, 180)
            self._canvas.setMaximumHeight(320)
            layout.addWidget(self._canvas, 1, Qt.AlignmentFlag.AlignCenter)
            self._empty_label = None
            self._wedges = []
            self._legend_obj = None
            self._empty_text = None
        else:
            self._fig = None
            self._ax = None
            self._canvas = None
            self._empty_label = QLabel("matplotlib 필요")
            self._wedges = []
            self._legend_obj = None
            self._empty_text = None
            layout.addWidget(self._empty_label)

        self.update_aggregator(None)

    def _draw_empty(self) -> None:
        """데이터 없음 상태: 기존 pie/범례 제거 후 텍스트만 표시."""
        for w in self._wedges:
            w.remove()
        self._wedges.clear()
        if self._legend_obj is not None:
            self._legend_obj.remove()
            self._legend_obj = None
        self._ax.set_xlim(0, 1)
        self._ax.set_ylim(0, 1)
        self._ax.axis("off")
        if self._empty_text is None:
            self._empty_text = self._ax.text(
                0.5, 0.5, "데이터 없음",
                ha="center", va="center", fontsize=10,
            )
        self._canvas.draw_idle()

    def _full_redraw(self, non_zero: list[tuple[str, int, str]]) -> None:
        """segment 개수/구성이 바뀐 경우에만 전체 다시 그리기."""
        self._empty_text = None
        for w in self._wedges:
            w.remove()
        self._wedges.clear()
        if self._legend_obj is not None:
            self._legend_obj.remove()
            self._legend_obj = None

        self._ax.clear()
        sizes = [s[1] for s in non_zero]
        colors = [s[2] for s in non_zero]
        wedges, _t, _a = self._ax.pie(
            sizes,
            labels=None,
            colors=colors,
            autopct="",
            startangle=90,
            wedgeprops=dict(width=0.5, edgecolor="white", linewidth=1.2),
        )
        self._wedges.extend(wedges)
        self._legend_obj = self._ax.legend(
            wedges,
            [f"{s[0]} {s[1]:,}" for s in non_zero],
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            fontsize=8,
        )
        self._ax.axis("equal")
        self._canvas.draw_idle()

    def update_aggregator(self, aggregator) -> None:
        if not _HAS_MATPLOTLIB or self._ax is None:
            return
        segments = _aggregator_to_segments(aggregator) if aggregator else []
        total = sum(s[1] for s in segments)
        if total <= 0:
            self._draw_empty()
            return

        non_zero = [(l, v, c) for l, v, c in segments if v > 0]
        if not non_zero:
            self._draw_empty()
            return

        # 동일 wedge 개수면 데이터만 갱신(각도·범례 텍스트)
        if len(self._wedges) == len(non_zero):
            sizes = [s[1] for s in non_zero]
            angles = _angles_from_sizes(sizes)
            for i, (wedge, (theta1, theta2)) in enumerate(zip(self._wedges, angles)):
                wedge.set_theta1(theta1)
                wedge.set_theta2(theta2)
            if self._legend_obj is not None:
                for j, t in enumerate(self._legend_obj.get_texts()):
                    if j < len(non_zero):
                        t.set_text(f"{non_zero[j][0]} {non_zero[j][1]:,}")
            self._canvas.draw_idle()
            return

        # 개수가 바뀌면 전체 다시 그리기
        self._full_redraw(non_zero)
