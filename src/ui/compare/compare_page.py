from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QMessageBox,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
)
from PyQt6.QtGui import QPainter
from PyQt6.QtPrintSupport import QPrinter

from src.domain.result.service import calculate_result
from src.domain.compare import build_breakdown, get_top_drivers
from .scenario_selector import ScenarioSelector
from .compare_table import CompareTable


class ComparePage(QWidget):
    """
    시나리오 비교 페이지
    """

    def __init__(self):
        super().__init__()
        self.scenario_a = None
        self.scenario_b = None
        self.scenario_dir = Path(__file__).resolve().parents[2] / "exports"
        self.scenario_dir.mkdir(parents=True, exist_ok=True)

        layout = QVBoxLayout(self)

        selectors = QHBoxLayout()
        self.selector_a = ScenarioSelector("시나리오 A")
        self.selector_b = ScenarioSelector("시나리오 B")
        self.selector_a.on_load(self.load_a)
        self.selector_b.on_load(self.load_b)
        selectors.addWidget(self.selector_a)
        selectors.addWidget(self.selector_b)
        layout.addLayout(selectors)

        self.compare_button = QPushButton("비교")
        self.compare_button.clicked.connect(self.compare)
        layout.addWidget(self.compare_button)

        self.export_button = QPushButton("비교 결과 PDF 저장")
        self.export_button.clicked.connect(self.export_compare_pdf)
        layout.addWidget(self.export_button)

        self.top_title = QLabel("증감 상위 3개 항목")
        self.top_title.setStyleSheet("font-weight: bold;")
        self.top_subtitle = QLabel("(B안 − A안 기준, 절대증감 큰 순)")
        self.top_message = QLabel("시나리오를 선택 후 비교를 실행하세요")
        self.top_table = QTableWidget(0, 5)
        self.top_table.setHorizontalHeaderLabels(
            ["항목", "A안", "B안", "증감(원)", "기여도(%)"]
        )
        self.top_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.top_title)
        layout.addWidget(self.top_subtitle)
        layout.addWidget(self.top_message)
        layout.addWidget(self.top_table)

        self.table = CompareTable()
        layout.addWidget(self.table)

        self.last_compare = None

    def load_a(self, scenario_id: str):
        self.scenario_a = self.selector_a.load_scenario(scenario_id)
        if not self.scenario_a:
            return
        QMessageBox.information(self, "시나리오 A", "불러오기 완료")

    def load_b(self, scenario_id: str):
        self.scenario_b = self.selector_b.load_scenario(scenario_id)
        if not self.scenario_b:
            return
        QMessageBox.information(self, "시나리오 B", "불러오기 완료")

    def compare(self):
        if not self.scenario_a or not self.scenario_b:
            QMessageBox.information(self, "비교", "시나리오 A/B를 모두 선택하세요.")
            return

        agg_a, labor_rows_a = self._run_pipeline(self.scenario_a)
        agg_b, labor_rows_b = self._run_pipeline(self.scenario_b)

        values_a, labels_a = build_breakdown(agg_a, labor_rows_a)
        values_b, labels_b = build_breakdown(agg_b, labor_rows_b)
        labels = {**labels_a, **labels_b}
        top_drivers = get_top_drivers(values_a, values_b, labels, 3)
        self._render_top_drivers(top_drivers, agg_a.grand_total, agg_b.grand_total)

        rows = []
        for key, label in [
            ("labor_total", "노무비 합계"),
            ("fixed_expense_total", "고정경비 합계"),
            ("variable_expense_total", "변동경비 합계"),
            ("passthrough_expense_total", "대행비 합계"),
            ("overhead_cost", "일반관리비"),
            ("profit", "이윤"),
            ("grand_total", "총계(VAT 제외)"),
        ]:
            a = getattr(agg_a, key)
            b = getattr(agg_b, key)
            rows.append(
                {
                    "label": label,
                    "a": a,
                    "b": b,
                    "delta": b - a,
                }
            )

        highlight_labels = {d["label"] for d in top_drivers}
        self.table.update_rows(rows, highlight_labels=highlight_labels)

        self.last_compare = {
            "scenario_a_name": self.scenario_a.get("scenario_id", "A안"),
            "scenario_b_name": self.scenario_b.get("scenario_id", "B안"),
            "agg_a": agg_a,
            "agg_b": agg_b,
            "rows": rows,
            "top_drivers": top_drivers,
        }

    def _run_pipeline(self, payload: dict):
        scenario_id = payload.get("scenario_id", "default")
        result = calculate_result(scenario_id, None)
        return result["aggregator"], result["labor_rows"]

    def _render_top_drivers(self, drivers: list[dict], a_total: int, b_total: int) -> None:
        total_delta = b_total - a_total
        self.top_table.setRowCount(0)

        if total_delta == 0:
            self.top_message.setText("변동 없음")
            return

        if not drivers:
            self.top_message.setText("변동 항목 3개 미만")
            return

        self.top_message.setText("")

        for d in drivers:
            row_idx = self.top_table.rowCount()
            self.top_table.insertRow(row_idx)

            status = "증가" if d["delta"] > 0 else "감소"
            label_text = f"{d['label']} ({status})"

            if total_delta != 0:
                share_pct = (d["delta"] / total_delta) * 100
            else:
                share_pct = 0.0

            self.top_table.setItem(row_idx, 0, QTableWidgetItem(label_text))
            self.top_table.setItem(row_idx, 1, QTableWidgetItem(f"{d['a']:,}"))
            self.top_table.setItem(row_idx, 2, QTableWidgetItem(f"{d['b']:,}"))
            self.top_table.setItem(row_idx, 3, QTableWidgetItem(f"{d['delta']:,}"))
            self.top_table.setItem(row_idx, 4, QTableWidgetItem(f"{share_pct:.1f}"))

    def export_compare_pdf(self):
        if not self.last_compare:
            QMessageBox.information(self, "내보내기", "먼저 비교를 실행하세요.")
            return

        scenario_a = self.last_compare["scenario_a_name"]
        scenario_b = self.last_compare["scenario_b_name"]
        safe_a = self._sanitize_filename(scenario_a)
        safe_b = self._sanitize_filename(scenario_b)

        from datetime import datetime

        date_str = datetime.now().strftime("%Y%m%d")
        default_name = f"scenario_compare_{safe_a}_vs_{safe_b}_{date_str}.pdf"
        default_path = self.scenario_dir / default_name

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "비교 결과 PDF 저장",
            str(default_path),
            "PDF Files (*.pdf)",
        )
        if not file_path:
            return

        printer = QPrinter()
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(file_path)

        painter = QPainter(printer)
        page_rect = printer.pageRect()
        left_x = page_rect.left() + 40
        right_x = page_rect.right() - 40
        y = 40
        line_height = 20

        def draw_line(text: str, bold: bool = False):
            nonlocal y
            font = painter.font()
            font.setBold(bold)
            painter.setFont(font)
            painter.drawText(left_x, y, text)
            y += line_height

        def draw_label_value(label: str, value_text: str, bold: bool = False):
            nonlocal y
            font = painter.font()
            font.setBold(bold)
            painter.setFont(font)
            painter.drawText(left_x, y, label)
            metrics = painter.fontMetrics()
            value_width = metrics.horizontalAdvance(value_text)
            painter.drawText(right_x - value_width, y, value_text)
            y += line_height

        agg_a = self.last_compare["agg_a"]
        agg_b = self.last_compare["agg_b"]
        rows = self.last_compare["rows"]
        top_drivers = self.last_compare["top_drivers"]

        draw_line("시나리오 비교 요약", bold=True)
        draw_line(f"A안: {scenario_a}")
        draw_line(f"B안: {scenario_b}")
        draw_line(f"작성일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        draw_line("")

        draw_line("[총계 비교]", bold=True)
        a_total = agg_a.grand_total
        b_total = agg_b.grand_total
        delta = b_total - a_total
        delta_pct = 0.0 if a_total == 0 else (delta / a_total * 100)
        draw_label_value("A안 총계(VAT 제외):", f"{a_total:,}")
        draw_label_value("B안 총계(VAT 제외):", f"{b_total:,}")
        draw_label_value("증감(B-A):", f"{delta:,}")
        draw_label_value("증감률:", f"{delta_pct:.1f}%")
        draw_line("")

        draw_line("[요약 비교 테이블]", bold=True)
        header = "항목"
        header_a = "A안"
        header_b = "B안"
        header_d = "증감(원)"
        metrics = painter.fontMetrics()
        painter.drawText(left_x, y, header)
        painter.drawText(right_x - 300, y, header_a)
        painter.drawText(right_x - 200, y, header_b)
        painter.drawText(right_x - 80, y, header_d)
        y += line_height
        label_map = {
            "대행비 합계": "대납비 합계",
        }
        for row in rows:
            label = label_map.get(row["label"], row["label"])
            if label == "총계(VAT 제외)":
                painter.fillRect(
                    left_x - 5,
                    y - line_height + 4,
                    right_x - left_x + 10,
                    line_height,
                    QColor(255, 243, 205),
                )
            painter.drawText(left_x, y, label)
            a_text = f"{row['a']:,}"
            b_text = f"{row['b']:,}"
            d_text = f"{row['delta']:,}"
            painter.drawText(right_x - 300, y, a_text)
            painter.drawText(right_x - 200, y, b_text)
            painter.drawText(right_x - 80, y, d_text)
            y += line_height
        draw_line("")

        draw_line("[증감 상위 3개 항목]", bold=True)
        if not top_drivers:
            draw_line("변동 없음")
        else:
            for d in top_drivers:
                share = ""
                if delta != 0:
                    share_pct = (d["delta"] / delta) * 100
                    share = f" ({share_pct:.1f}%)"
                label = d["label"]
                a_text = f"{d['a']:,}"
                b_text = f"{d['b']:,}"
                d_text = f"{d['delta']:,}{share}"
                painter.drawText(left_x, y, label)
                painter.drawText(right_x - 300, y, a_text)
                painter.drawText(right_x - 200, y, b_text)
                painter.drawText(right_x - 80, y, d_text)
                y += line_height
        draw_line("")
        draw_line("본 비교 결과는 VAT 제외 기준입니다.", bold=True)

        painter.end()
        QMessageBox.information(self, "내보내기", "PDF 저장이 완료되었습니다.")

    def _sanitize_filename(self, name: str) -> str:
        safe = "".join(ch for ch in name if ch.isalnum() or ch in ("-", "_"))
        return safe or "scenario"
