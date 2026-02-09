import json
import logging
import traceback
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QFileDialog,
    QMessageBox,
    QTabWidget,
    QAbstractItemDelegate,
)
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPainter
from PyQt6.QtPrintSupport import QPrinter

import os
from src.domain.db import get_connection, startup_verification
from src.domain.masterdata.repo import MasterDataRepo
from src.domain.migration_runner import run_migrations
from src.domain.result.service import calculate_result, get_result_snapshot
from src.domain.scenario_input.service import (
    ScenarioInputValidationError,
    post_scenario_input,
    get_scenario_input,
)
from .input_panel import InputPanel
from .summary_panel import SummaryPanel
from .labor_detail_table import LaborDetailTable
from .expense_detail_table import ExpenseDetailTable
from .compare.compare_page import ComparePage
from .job_role_table import JobRoleTable, setup_qtable_debug_log
from .expense_input_table import ExpenseInputTable
from .state import build_canonical_input, compute_action_state
from .export_helpers import build_job_breakdown_rows, build_top_job_summary, build_detail_job_rows, TOP_N_JOB_ROLES


def safe_run_save(fn):
    """저장 동작을 감싸서 앱이 죽지 않게 하고, 예외를 로그+팝업으로 남김."""
    try:
        return fn()
    except Exception as exc:
        msg = f"[SAVE ERROR] {exc}\n\n{traceback.format_exc()}"
        logging.error(msg)
        QMessageBox.critical(None, "저장 실패", msg)
        return None


def commit_table_edit(table) -> None:
    if table is None:
        return
    editor = table.focusWidget()
    if editor is not None and editor is not table:
        table.closeEditor(editor, QAbstractItemDelegate.EndEditHint.SubmitModelCache)
    table.clearFocus()


def extract_table_rows(table, columns: dict) -> list[dict]:
    rows = []
    if table is None:
        return rows
    for row in range(table.rowCount()):
        row_data = {}
        for key, col in columns.items():
            if col >= table.columnCount():
                row_data[key] = ""
                continue
            item = table.item(row, col)
            row_data[key] = item.text() if item is not None else ""
        rows.append(row_data)
    return rows


def save_json(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


class MainWindow(QWidget):
    """
    최소 집계 UI
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("원가산정 집계")

        layout = QVBoxLayout(self)
        setup_qtable_debug_log("logs/qtable_input_debug.log")
        startup_verification(bool(os.environ.get("COSTCALC_DEBUG")))

        self.input_panel = InputPanel()
        self.job_role_table = JobRoleTable()
        self.expense_input_table = ExpenseInputTable()
        self.summary_panel = SummaryPanel()
        self.labor_detail = LaborDetailTable()
        self.expense_detail = ExpenseDetailTable()
        self.calculate_button = QPushButton("집계 실행")
        self.save_button = QPushButton("시나리오 저장")
        self.load_button = QPushButton("시나리오 불러오기")
        self.export_pdf_button = QPushButton("요약 PDF 내보내기")
        self.export_excel_button = QPushButton("상세 Excel 내보내기")
        self.test_data_button = QPushButton("Pre-fill Test Data")
        self.sample_data_button = QPushButton("Sample Data")
        self.calculate_button.clicked.connect(self.calculate)
        self.save_button.clicked.connect(self.save_scenario)
        self.load_button.clicked.connect(self.load_scenario)
        self.export_pdf_button.clicked.connect(self.export_summary_pdf)
        self.export_excel_button.clicked.connect(self.export_details_excel)
        self.test_data_button.clicked.connect(self._prefill_test_data)
        self.sample_data_button.clicked.connect(self._fill_sample_data)

        self.scenario_dir = Path(__file__).resolve().parents[2] / "scenarios"
        self.scenario_dir.mkdir(parents=True, exist_ok=True)

        top_row = QHBoxLayout()
        left_panel = QVBoxLayout()
        left_panel.addWidget(self.input_panel)
        left_panel.addWidget(self.job_role_table)
        left_panel.addWidget(self.expense_input_table)
        left_panel_widget = QWidget()
        left_panel_widget.setLayout(left_panel)
        top_row.addWidget(left_panel_widget)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.summary_panel, "요약")
        self.tabs.addTab(self.labor_detail, "노무비 상세")
        self.tabs.addTab(self.expense_detail, "경비 상세")
        self.tabs.addTab(ComparePage(), "시나리오 비교")
        self.tabs.currentChanged.connect(lambda _: self._force_editable_inputs())
        top_row.addWidget(self.tabs)

        layout.addLayout(top_row)
        button_row = QHBoxLayout()
        button_row.addWidget(self.calculate_button)
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.load_button)
        button_row.addWidget(self.export_pdf_button)
        button_row.addWidget(self.export_excel_button)
        button_row.addWidget(self.test_data_button)
        button_row.addWidget(self.sample_data_button)
        layout.addLayout(button_row)

        self._refresh_master_data("default")
        self.last_aggregator = None
        self.last_scenario_name = ""
        self.last_scenario_id = ""
        self.last_labor_rows = []
        self.last_expense_rows = []
        self._role_name_map = {}
        self._dirty = False

        self.input_panel.on_change(self._mark_dirty)
        self.job_role_table.on_change(self._mark_dirty)
        self.expense_input_table.on_change(self._mark_dirty)
        self._refresh_button_state()
        QTimer.singleShot(0, self._force_editable_inputs)
        QTimer.singleShot(200, self._force_editable_inputs)

    def _force_editable_inputs(self) -> None:
        commit_table_edit(self.job_role_table.table)
        commit_table_edit(self.expense_input_table.table)
        self.job_role_table._force_editable()
        self.expense_input_table._force_editable()

    def _prefill_test_data(self) -> None:
        commit_table_edit(self.job_role_table.table)
        commit_table_edit(self.expense_input_table.table)

        self.job_role_table.table.setRowCount(0)
        self.expense_input_table.table.setRowCount(0)

        sample_counts = [2, 1, 1]
        for idx, count in enumerate(sample_counts):
            self.job_role_table.add_empty_row()
            row = self.job_role_table.table.rowCount() - 1
            roles = getattr(self.job_role_table, "_available_roles", [])
            if idx < len(roles):
                job_code = roles[idx]["job_code"]
                combo = self.job_role_table.table.cellWidget(row, 0)
                if combo is not None:
                    combo.setCurrentText(job_code)
            self.job_role_table.table.item(row, 6).setText(str(count))

        sample_qty = [3, 5]
        for idx, qty in enumerate(sample_qty):
            self.expense_input_table.add_empty_row()
            row = self.expense_input_table.table.rowCount() - 1
            items = getattr(self.expense_input_table, "_available_items", [])
            if idx < len(items):
                exp_code = items[idx]["exp_code"]
                combo = self.expense_input_table.table.cellWidget(row, 0)
                if combo is not None:
                    combo.setCurrentText(exp_code)
            self.expense_input_table.table.item(row, 5).setText(str(qty))

        self.job_role_table.dirty = True
        self.expense_input_table.dirty = True
        self._set_dirty(True)
        self.save_scenario()
        self.calculate()

    def _fill_sample_data(self) -> None:
        commit_table_edit(self.job_role_table.table)
        job_inputs = self.job_role_table.get_job_inputs()
        samples = {
            "JOB_DRIVER": {"work_days": 22, "work_hours": 8, "headcount": 2},
            "JOB_OPERATOR": {"work_days": 20, "work_hours": 8, "headcount": 1},
        }
        for job_code, values in samples.items():
            if job_code in job_inputs:
                job_inputs[job_code].update(values)
        self.job_role_table.set_job_inputs(job_inputs)
        self.job_role_table.dirty = True
        self._set_dirty(True)
        self.save_scenario()

    def calculate(self):
        if self.job_role_table.dirty or self.expense_input_table.dirty:
            logging.warning("[REFRESH] skipped: editing/dirty")
            return
        if self._dirty:
            QMessageBox.information(self, "집계", "저장되지 않은 변경사항이 있습니다. 먼저 저장하세요.")
            return
        commit_table_edit(self.job_role_table.table)
        commit_table_edit(self.expense_input_table.table)
        _ = self.job_role_table.get_job_inputs()
        _ = self.expense_input_table.get_items()

        values = self.input_panel.get_values()
        scenario_name = values["scenario_name"] or "default"
        scenario_id = self._sanitize_filename(scenario_name)
        self._refresh_master_data(scenario_id)

        conn = get_connection()
        try:
            result = calculate_result(scenario_id, conn)
        finally:
            conn.close()

        aggregator = result["aggregator"]
        self.summary_panel.update_summary(aggregator, pdf_grand_total=0)
        self.labor_detail.update_rows(result["labor_rows"])
        self.expense_detail.update_rows(result["expense_rows"])
        self.summary_panel.update()
        self.labor_detail.update()
        self.expense_detail.update()

        self.last_aggregator = aggregator
        self.last_scenario_name = scenario_name
        self.last_scenario_id = scenario_id
        self.last_labor_rows = result["labor_rows"]
        self.last_expense_rows = result["expense_rows"]
        self._refresh_button_state()

    def save_scenario(self):
        return safe_run_save(self._save_scenario_impl)

    def _save_scenario_impl(self):
        commit_table_edit(self.job_role_table.table)
        commit_table_edit(self.expense_input_table.table)
        values = self.input_panel.get_values()
        scenario_name = values.get("scenario_name") or "default"
        scenario_id = self._sanitize_filename(scenario_name)
        if not scenario_id:
            QMessageBox.information(self, "저장", "시나리오명을 입력하세요.")
            return

        data = extract_table_rows(
            self.job_role_table.table,
            {"job_code": 0, "job_name": 1, "headcount": 2, "remark": 3, "use_yn": 4, "sort_order": 5},
        )
        logging.info("[SAVE] extracted job_role rows = %s", len(data))
        save_json(str(self.scenario_dir / f"{scenario_id}_job_roles.json"), data)

        conn = get_connection()
        try:
            run_migrations(conn)
            ui_data = {
                "job_inputs": self.job_role_table.get_job_inputs(),
                "expense_inputs": self.expense_input_table.get_items(),
            }
            logging.debug("DEBUG UI DATA: %s", ui_data)
            payload = build_canonical_input(
                ui_data["job_inputs"],
                ui_data["expense_inputs"],
            )
            post_scenario_input(payload, scenario_id, conn)
        except ScenarioInputValidationError as exc:
            self._show_validation_errors(exc.errors)
            return
        finally:
            conn.close()

        self.last_scenario_name = scenario_name
        self.last_scenario_id = scenario_id
        self._set_dirty(False)
        self.job_role_table.dirty = False
        self.expense_input_table.dirty = False
        QMessageBox.information(self, "저장 완료", "시나리오가 저장되었습니다.")

    def load_scenario(self):
        if self.job_role_table.is_editing() or self.expense_input_table.is_editing():
            logging.warning("[REFRESH] skipped: editing/dirty")
            return
        if self.job_role_table.dirty or self.expense_input_table.dirty:
            logging.warning("[REFRESH] skipped: editing/dirty")
            return
        values = self.input_panel.get_values()
        scenario_name = values.get("scenario_name") or "default"
        scenario_id = self._sanitize_filename(scenario_name)
        if not scenario_id:
            QMessageBox.information(self, "불러오기", "시나리오명을 입력하세요.")
            return

        conn = get_connection()
        try:
            canonical = get_scenario_input(scenario_id, conn)
        finally:
            conn.close()

        self._refresh_master_data(scenario_id)
        self._apply_canonical_input(canonical)
        self.last_scenario_id = scenario_id
        self.last_scenario_name = scenario_name
        self._set_dirty(False)
        self.job_role_table._force_editable()
        self.expense_input_table._force_editable()

    def _sanitize_filename(self, name: str) -> str:
        safe = "".join(ch for ch in name if ch.isalnum() or ch in ("-", "_"))
        return safe or "scenario"

    def _refresh_master_data(self, scenario_id: str) -> None:
        if self.job_role_table.is_editing() or self.expense_input_table.is_editing():
            logging.warning("[REFRESH] skipped: editing/dirty")
            return
        if self.job_role_table.dirty or self.expense_input_table.dirty:
            logging.warning("[REFRESH] skipped: editing/dirty")
            return
        commit_table_edit(self.job_role_table.table)
        commit_table_edit(self.expense_input_table.table)
        _ = self.job_role_table.get_job_inputs()
        _ = self.expense_input_table.get_items()
        conn = get_connection()
        repo = MasterDataRepo(conn)
        try:
            roles = repo.get_job_roles(scenario_id)
            items = repo.get_expense_items(scenario_id)
            prices = {
                p.exp_code: {"unit_price": p.unit_price, "unit": p.unit}
                for p in repo.get_expense_pricebook(scenario_id)
            }
            self._role_name_map = {r.job_code: r.job_name for r in roles}
            self.job_role_table.table.blockSignals(True)
            self.expense_input_table.table.blockSignals(True)
            try:
                self.job_role_table.load_roles(
                    [{"job_code": r.job_code, "job_name": r.job_name} for r in roles],
                    default_work_days=20.6,
                    default_work_hours=8.0,
                )
                self.job_role_table.set_available_roles(
                    [{"job_code": r.job_code, "job_name": r.job_name} for r in roles]
                )
                self.expense_input_table.load_items(
                    [
                        {
                            "exp_code": i.exp_code,
                            "exp_name": i.exp_name,
                            "group_code": i.group_code,
                            "sort_order": i.sort_order,
                        }
                        for i in items
                    ],
                    prices,
                )
                self.expense_input_table.set_available_items(
                    [
                        {
                            "exp_code": i.exp_code,
                            "exp_name": i.exp_name,
                            "group_code": i.group_code,
                            "sort_order": i.sort_order,
                        }
                        for i in items
                    ],
                    prices,
                )
            finally:
                self.job_role_table.table.blockSignals(False)
                self.expense_input_table.table.blockSignals(False)
        finally:
            conn.close()

    def export_summary_pdf(self):
        return safe_run_save(self._export_summary_pdf_impl)

    def _export_summary_pdf_impl(self):
        if self._dirty:
            QMessageBox.information(self, "내보내기", "저장되지 않은 변경사항이 있습니다.")
            return
        snapshot = get_result_snapshot(self.last_scenario_id)
        if snapshot is None:
            QMessageBox.information(self, "내보내기", "계산 결과가 없습니다. 먼저 집계를 실행하세요.")
            return

        safe_name = self._sanitize_filename(self.last_scenario_name)
        default_path = self.scenario_dir / f"{safe_name}_summary.pdf"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "요약 PDF 내보내기",
            str(default_path),
            "PDF Files (*.pdf)",
        )
        if not file_path:
            return

        printer = QPrinter()
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(file_path)

        painter = QPainter(printer)
        y = 40
        line_height = 24

        def draw_line(text: str):
            nonlocal y
            painter.drawText(40, y, text)
            y += line_height

        aggregator = snapshot.get("aggregator", {})
        draw_line(f"시나리오: {self.last_scenario_name}")
        draw_line("집계 요약")
        draw_line(f"노무비 합계: {aggregator.get('labor_total', 0):,}")
        draw_line(f"고정경비 합계: {aggregator.get('fixed_expense_total', 0):,}")
        draw_line(f"변동경비 합계: {aggregator.get('variable_expense_total', 0):,}")
        draw_line(f"대행비 합계: {aggregator.get('passthrough_expense_total', 0):,}")
        draw_line(f"일반관리비: {aggregator.get('overhead_cost', 0):,}")
        draw_line(f"이윤: {aggregator.get('profit', 0):,}")
        draw_line(f"총계(VAT 제외): {aggregator.get('grand_total', 0):,}")

        draw_line("")
        draw_line(f"직무별 노무비 상위 {TOP_N_JOB_ROLES}")
        for job_name, total, _ in build_top_job_summary(snapshot, TOP_N_JOB_ROLES):
            draw_line(f"{job_name}: {total:,}")

        painter.end()

        detail_path = file_path.replace("_summary.pdf", "_detail.pdf")
        self._export_detail_pdf(detail_path, snapshot)
        QMessageBox.information(self, "내보내기", "PDF 저장이 완료되었습니다.")

    def export_details_excel(self):
        return safe_run_save(self._export_details_excel_impl)

    def _export_details_excel_impl(self):
        if self._dirty:
            QMessageBox.information(self, "내보내기", "저장되지 않은 변경사항이 있습니다.")
            return
        snapshot = get_result_snapshot(self.last_scenario_id)
        if snapshot is None:
            QMessageBox.information(self, "내보내기", "계산 결과가 없습니다. 먼저 집계를 실행하세요.")
            return

        try:
            import openpyxl
        except ImportError:
            QMessageBox.warning(
                self,
                "내보내기 실패",
                "openpyxl이 설치되어 있지 않습니다. `pip install openpyxl` 실행 후 다시 시도하세요.",
            )
            return

        safe_name = self._sanitize_filename(self.last_scenario_name)
        default_path = self.scenario_dir / f"{safe_name}_details.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "상세 Excel 내보내기",
            str(default_path),
            "Excel Files (*.xlsx)",
        )
        if not file_path:
            return

        wb = openpyxl.Workbook()

        ws_summary = wb.active
        ws_summary.title = "Summary"
        ws_summary.append(["항목", "값"])
        aggregator = snapshot.get("aggregator", {})
        ws_summary.append(["labor_total", aggregator.get("labor_total", 0)])
        ws_summary.append(["fixed_expense_total", aggregator.get("fixed_expense_total", 0)])
        ws_summary.append(["variable_expense_total", aggregator.get("variable_expense_total", 0)])
        ws_summary.append(["passthrough_expense_total", aggregator.get("passthrough_expense_total", 0)])
        ws_summary.append(["overhead_cost", aggregator.get("overhead_cost", 0)])
        ws_summary.append(["profit", aggregator.get("profit", 0)])
        ws_summary.append(["grand_total", aggregator.get("grand_total", 0)])

        ws_labor = wb.create_sheet("Labor Detail")
        ws_labor.append(
            ["role", "headcount", "base_salary", "allowances", "insurance_total", "labor_subtotal", "role_total"]
        )
        for row in snapshot.get("labor_rows", []):
            ws_labor.append(
                [
                    row["role"],
                    row["headcount"],
                    row["base_salary"],
                    row["allowances"],
                    row["insurance_total"],
                    row["labor_subtotal"],
                    row["role_total"],
                ]
            )

        ws_expense = wb.create_sheet("Expense Detail")
        ws_expense.append(["category", "name", "driver", "unit_cost", "quantity", "row_total", "type"])
        for row in snapshot.get("expense_rows", []):
            ws_expense.append(
                [
                    row["category"],
                    row["name"],
                    row["driver"],
                    row["unit_cost"],
                    row["quantity"],
                    row["row_total"],
                    row["type"],
                ]
            )

        ws_job = wb.create_sheet("노무비_직종상세")
        ws_job.append(
            [
                "job_code",
                "job_name",
                "headcount",
                "work_days",
                "base_wage",
                "allowance",
                "overtime",
                "total",
            ]
        )
        for row in build_job_breakdown_rows(snapshot):
            ws_job.append(row)

        wb.save(file_path)
        QMessageBox.information(self, "내보내기", "Excel 저장이 완료되었습니다.")

    def _export_detail_pdf(self, file_path: str, snapshot: dict) -> None:
        if not file_path:
            return

        printer = QPrinter()
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(file_path)

        painter = QPainter(printer)
        y = 40
        line_height = 22

        def draw_line(text: str):
            nonlocal y
            painter.drawText(40, y, text)
            y += line_height

        draw_line(f"시나리오: {self.last_scenario_name}")
        draw_line("노무비 직종 상세")
        draw_line("job_code | job_name | headcount | work_days | base_wage | allowance | overtime | total")

        for row in build_detail_job_rows(snapshot):
            draw_line(" | ".join(str(v) for v in row))

        painter.end()

    def _apply_canonical_input(self, canonical: dict) -> None:
        self.job_role_table.table.blockSignals(True)
        self.expense_input_table.table.blockSignals(True)
        try:
            labor_inputs = canonical.get("labor", {}).get("job_roles", {})
            expense_inputs = canonical.get("expenses", {}).get("items", {})
            self.job_role_table.set_job_inputs(labor_inputs)
            self.expense_input_table.set_items(expense_inputs)
        finally:
            self.job_role_table.table.blockSignals(False)
            self.expense_input_table.table.blockSignals(False)

    def _mark_dirty(self):
        self._set_dirty(True)

    def _set_dirty(self, value: bool):
        self._dirty = value
        self._refresh_button_state()

    def _refresh_button_state(self):
        state = compute_action_state(self._dirty, self.last_aggregator is not None)
        self.save_button.setEnabled(state["save_enabled"])
        self.calculate_button.setEnabled(state["calculate_enabled"])
        self.export_pdf_button.setEnabled(state["export_enabled"])
        self.export_excel_button.setEnabled(state["export_enabled"])

    def _show_validation_errors(self, errors):
        lines = [f"{e.field_path}: {e.message}" for e in errors]
        QMessageBox.warning(self, "검증 오류", "\n".join(lines))
