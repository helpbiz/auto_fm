import logging
import os
import re
import traceback
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QAbstractItemDelegate,
    QComboBox,
    QLineEdit,
    QStyledItemDelegate,
)
from PyQt6.QtCore import Qt, QTimer, QObject, QEvent
from PyQt6.QtGui import QDoubleValidator

from src.domain.constants.job_data import get_job_mapping_from_file

COL_JOB_CODE = 0
COL_JOB_NAME = 1
COL_GRADE = 2   # 직종 (job_mapping grade, 읽기 전용)
COL_WORK_DAYS = 3
COL_WORK_HOURS = 4
COL_OVERTIME_HOURS = 5
COL_HOLIDAY_HOURS = 6
COL_HEADCOUNT = 7
COL_MAX = 7

_LOG_READY = False


def setup_qtable_debug_log(log_path: str) -> str:
    global _LOG_READY
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    if not _LOG_READY:
        logging.basicConfig(
            filename=log_path,
            level=logging.DEBUG,
            format="%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            encoding="utf-8",
        )
        _LOG_READY = True
    return log_path


def _dump_table_state(tag: str, table: QTableWidget) -> None:
    try:
        vp = table.viewport()
        fw = table.window().focusWidget() if table.window() else None
        focus_policy = table.focusPolicy()
        state_val = table.state()
        selection_mode = table.selectionMode()
        vp_focus_policy = vp.focusPolicy()
        vp_cursor = vp.cursor().shape()
        logging.debug(
            "[%s] enabled(t=%s vp=%s) visible(t=%s vp=%s) focusPolicy=%s (%s) hasFocus=%s focusWidget=%s editTriggers=%s (%s) state=%s (%s) selectionMode=%s (%s) current=(%s,%s) blockSignals=%s updatesEnabled=%s",
            tag,
            table.isEnabled(),
            vp.isEnabled(),
            table.isVisible(),
            vp.isVisible(),
            repr(focus_policy),
            _to_int_safe(focus_policy),
            table.hasFocus(),
            type(fw).__name__ if fw else None,
            repr(table.editTriggers()),
            _to_int_safe(table.editTriggers()),
            repr(state_val),
            _to_int_safe(state_val),
            repr(selection_mode),
            _to_int_safe(selection_mode),
            table.currentRow(),
            table.currentColumn(),
            table.signalsBlocked(),
            table.updatesEnabled(),
        )
        logging.debug(
            "[%s] viewportAcceptDrops=%s viewportFocusPolicy=%s (%s) viewportCursor=%s (%s)",
            tag,
            vp.acceptDrops(),
            repr(vp_focus_policy),
            _to_int_safe(vp_focus_policy),
            repr(vp_cursor),
            _to_int_safe(vp_cursor),
        )
    except Exception:
        logging.error("[%s] dump failed:\n%s", tag, traceback.format_exc())


class ViewportEventLogger(QObject):
    def __init__(self, table: QTableWidget, name: str = "table"):
        super().__init__(table)
        self.table = table
        self.name = name

    def eventFilter(self, obj, ev):  # noqa: N802
        et = ev.type()
        watch = {
            QEvent.Type.MouseButtonPress,
            QEvent.Type.MouseButtonDblClick,
            QEvent.Type.KeyPress,
            QEvent.Type.FocusIn,
            QEvent.Type.FocusOut,
            QEvent.Type.EnabledChange,
            QEvent.Type.Show,
            QEvent.Type.Hide,
        }
        if et in watch:
            info = f"{self.name} ev={int(et)} {ev.__class__.__name__}"
            if et in (QEvent.Type.KeyPress,):
                info += f" key={getattr(ev,'key',lambda:None)()} text='{getattr(ev,'text',lambda:'')()}'"
            if et in (QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonDblClick):
                pos = getattr(ev, "pos", lambda: None)()
                info += f" pos={pos}"
            logging.debug(info)
        return False


def attach_table_debug_hooks(table: QTableWidget, name: str = "qtable") -> None:
    if hasattr(table, "_vp_logger"):
        return
    vp_logger = ViewportEventLogger(table, name=name)
    table.viewport().installEventFilter(vp_logger)
    table.itemDoubleClicked.connect(
        lambda it: logging.debug(f"{name} signal: itemDoubleClicked r={it.row()} c={it.column()}")
    )
    table.itemClicked.connect(
        lambda it: logging.debug(f"{name} signal: itemClicked r={it.row()} c={it.column()}")
    )
    table.itemActivated.connect(
        lambda it: logging.debug(f"{name} signal: itemActivated r={it.row()} c={it.column()}")
    )
    table.currentCellChanged.connect(
        lambda r, c, pr, pc: logging.debug(f"{name} signal: currentCellChanged ({pr},{pc})->({r},{c})")
    )
    table.itemChanged.connect(
        lambda it: logging.debug(f"{name} signal: itemChanged r={it.row()} c={it.column()} text='{it.text()}'")
    )
    table.installEventFilter(vp_logger)
    table._vp_logger = vp_logger


def _to_int_safe(value) -> int | None:
    try:
        return int(value)
    except Exception:
        pass
    if hasattr(value, "value"):
        try:
            return int(value.value)
        except Exception:
            pass
    return None


def hook_suspicious_methods(table: QTableWidget, name: str = "qtable") -> None:
    if hasattr(table, "_suspicious_hooked"):
        return
    orig_set_enabled = table.setEnabled
    orig_set_edit_triggers = table.setEditTriggers
    orig_vp_set_enabled = table.viewport().setEnabled

    def set_enabled_hook(val: bool):
        logging.debug(f"{name}.setEnabled({val}) called")
        return orig_set_enabled(val)

    def set_edit_triggers_hook(val):
        v_int = _to_int_safe(val)
        v_repr = repr(val)
        logging.debug(
            "%s.setEditTriggers(val=%s, int=%s) called!", name, v_repr, v_int
        )
        return orig_set_edit_triggers(val)

    def vp_set_enabled_hook(val: bool):
        logging.debug(f"{name}.viewport().setEnabled({val}) called")
        return orig_vp_set_enabled(val)

    table.setEnabled = set_enabled_hook
    table.setEditTriggers = set_edit_triggers_hook
    table.viewport().setEnabled = vp_set_enabled_hook
    table._suspicious_hooked = True


def _force_editable_full(table: QTableWidget, tag: str = "force") -> None:
    if table.columnCount() == 0:
        table.setColumnCount(2)
    table.setEnabled(True)
    table.setDisabled(False)
    table.viewport().setEnabled(True)
    table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    table.viewport().setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    table.setEditTriggers(
        QAbstractItemView.EditTrigger.DoubleClicked
        | QAbstractItemView.EditTrigger.SelectedClicked
        | QAbstractItemView.EditTrigger.EditKeyPressed
        | QAbstractItemView.EditTrigger.AnyKeyPressed
    )
    if table.rowCount() == 0:
        table.setRowCount(1)
    for row in range(table.rowCount()):
        for col in range(table.columnCount()):
            item = table.item(row, col)
            if item is None:
                table.setItem(row, col, QTableWidgetItem(""))
            item = table.item(row, col)
            item.setFlags(
                Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsEditable
            )
    table.setFocus()
    table.setCurrentCell(0, 0)
    item00 = table.item(0, 0)
    flags00 = item00.flags() if item00 is not None else None
    et = table.editTriggers()
    et_int = _to_int_safe(et)
    logging.debug(
        "[%s] enabled=%s viewport_enabled=%s rows=%s cols=%s editTriggers=%s (%s) item00=%s flags00=%s (%s)",
        tag,
        table.isEnabled(),
        table.viewport().isEnabled(),
        table.rowCount(),
        table.columnCount(),
        repr(et),
        et_int,
        item00 is not None,
        repr(flags00),
        _to_int_safe(flags00),
    )
    _dump_table_state(f"{tag}:immediate", table)
    QTimer.singleShot(0, lambda: _dump_table_state(f"{tag}:after0ms", table))
    QTimer.singleShot(200, lambda: _dump_table_state(f"{tag}:after200ms", table))


class JobRoleTableWidget(QTableWidget):
    def closeEditor(self, editor, hint) -> None:
        if editor is not None:
            try:
                self.commitData(editor)
            except Exception:
                logging.debug("JOB_TABLE commitData failed:\n%s", traceback.format_exc())
        super().closeEditor(editor, hint)

    def mousePressEvent(self, event) -> None:
        super().mousePressEvent(event)
        index = self.indexAt(event.position().toPoint())
        if not index.isValid():
            return
        row = index.row()
        col = index.column()
        item = self.item(row, col)
        if item is None:
            self._ensure_row_items(row)
            item = self.item(row, col)
        if item is not None and (item.flags() & Qt.ItemFlag.ItemIsEditable):
            self.setCurrentCell(row, col)
            self.editItem(item)
            logging.debug("JOB_TABLE click edit row=%s col=%s", row, col)

    def keyPressEvent(self, event) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            row = self.currentRow()
            col = self.currentColumn()
            logging.debug("JOB_TABLE enter at row=%s col=%s", row, col)

            if row < 0 or col < 0:
                return super().keyPressEvent(event)

            editor = self.focusWidget()
            if editor is not None and editor is not self:
                self.closeEditor(editor, QAbstractItemDelegate.EndEditHint.SubmitModelCache)

            if col < COL_HEADCOUNT:
                self._ensure_row_items(row)
                self._set_job_name_readonly(row)
                self._set_grade_readonly(row)
                # 입력 가능한 컬럼만 이동: 직무코드(0) → 인원(7)
                next_col = col + 1
                while next_col < COL_HEADCOUNT:
                    it = self.item(row, next_col)
                    if it is not None and (it.flags() & Qt.ItemFlag.ItemIsEditable):
                        break
                    next_col += 1
                if next_col >= COL_HEADCOUNT:
                    next_col = COL_HEADCOUNT
                self.setCurrentCell(row, next_col)
                self.editItem(self.item(row, next_col))
                logging.debug("JOB_TABLE move to row=%s col=%s", row, next_col)
                return

            if col == COL_HEADCOUNT:
                self._ensure_row_items(row)
                self._set_job_name_readonly(row)
                self._set_grade_readonly(row)
                job_code = (self.item(row, COL_JOB_CODE).text() or "").strip()
                headcount = (self.item(row, COL_HEADCOUNT).text() or "").strip()
                valid = bool(job_code) and bool(headcount)
                logging.debug("JOB_TABLE row valid=%s", valid)
                if valid:
                    next_row = row + 1
                    if next_row >= self.rowCount():
                        self.insertRow(next_row)
                        logging.debug("JOB_TABLE inserted row=%s", next_row)
                    self._ensure_row_items(next_row)
                    self._set_job_name_readonly(next_row)
                    self._set_grade_readonly(next_row)
                    self.setCurrentCell(next_row, COL_JOB_CODE)
                    self.editItem(self.item(next_row, COL_JOB_CODE))
                    logging.debug("JOB_TABLE move to row=%s col=%s", next_row, COL_JOB_CODE)
                    return
                self.setCurrentCell(row, COL_HEADCOUNT)
                self.editItem(self.item(row, COL_HEADCOUNT))
                logging.debug("JOB_TABLE stay on row=%s col=%s", row, COL_HEADCOUNT)
                return

        super().keyPressEvent(event)

    def _ensure_row_items(self, row: int) -> None:
        for col in range(COL_MAX + 1):
            if self.item(row, col) is None:
                self.setItem(row, col, QTableWidgetItem(""))

    def _set_job_name_readonly(self, row: int) -> None:
        item = self.item(row, COL_JOB_NAME)
        if item is None:
            item = QTableWidgetItem("")
            self.setItem(row, COL_JOB_NAME, item)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

    def _set_grade_readonly(self, row: int) -> None:
        item = self.item(row, COL_GRADE)
        if item is None:
            item = QTableWidgetItem("")
            self.setItem(row, COL_GRADE, item)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)


class FloatItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, max_value: float = 1_000_000.0):
        super().__init__(parent)
        self._validator = QDoubleValidator(0.0, max_value, 4)
        self._validator.setNotation(QDoubleValidator.Notation.StandardNotation)

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setValidator(self._validator)
        return editor

    def setModelData(self, editor, model, index):
        super().setModelData(editor, model, index)
        panel = getattr(self.parent(), "parent", lambda: None)()
        if panel is not None and getattr(panel, "_external_on_change", None):
            QTimer.singleShot(0, panel._external_on_change)


class JobCodeComboDelegate(QStyledItemDelegate):
    """직무코드 컬럼 전용: 편집 시 QComboBox로 선택, 평소에는 셀 텍스트로만 표시."""

    def __init__(self, job_role_panel: "JobRoleTable"):
        super().__init__(job_role_panel.table)
        self._panel = job_role_panel

    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        combo.setMinimumWidth(120)
        combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        combo.addItem("")
        for role in self._panel._available_roles:
            combo.addItem(role["job_code"])
        return combo

    def setEditorData(self, editor, index):
        value = index.data(Qt.ItemDataRole.EditRole) or ""
        if isinstance(value, str):
            idx = editor.findText(value)
            editor.setCurrentIndex(idx if idx >= 0 else 0)

    def setModelData(self, editor, model, index):
        text = (editor.currentText() or "").strip()
        model.setData(index, text, Qt.ItemDataRole.EditRole)
        if self._panel._external_on_change:
            QTimer.singleShot(0, self._panel._external_on_change)


class JobRoleTable(QWidget):
    """
    직무별 입력 테이블 (표준은 읽기 전용)
    """
    # 클래스 상수로 플래그 정의
    EDITABLE_FLAGS = (
        Qt.ItemFlag.ItemIsSelectable
        | Qt.ItemFlag.ItemIsEnabled
        | Qt.ItemFlag.ItemIsEditable
    )
    READONLY_FLAGS = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self._loading = False
        self.dirty = False
        self._external_on_change = None
        self._available_roles: list[dict] = []
        self._role_name_map: dict[str, str] = {}

        title = QLabel("직무별 인원 입력")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)

        self.table = JobRoleTableWidget(0, 8)
        self.table.setItemDelegateForColumn(COL_JOB_CODE, JobCodeComboDelegate(self))
        float_delegate = FloatItemDelegate(self.table)
        for col in range(COL_WORK_DAYS, COL_HEADCOUNT + 1):
            self.table.setItemDelegateForColumn(col, float_delegate)
        self.table.setHorizontalHeaderLabels(
            [
                "직무코드",
                "직무명",
                "직종",
                "근무일수",
                "근무시간",
                "연장시간",
                "휴일근로일수",
                "인원",
            ]
        )
        self.table.horizontalHeader().setMinimumSectionSize(80)
        self.table.setColumnWidth(COL_JOB_CODE, 140)
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.SelectedClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
            | QAbstractItemView.EditTrigger.AnyKeyPressed
        )
        self.table.setEnabled(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        attach_table_debug_hooks(self.table, name="job_table")
        hook_suspicious_methods(self.table, name="job_table")
        self.table.itemChanged.connect(self._handle_item_changed)
        self._force_editable()
        layout.addWidget(self.table)

    def load_roles(self, roles: list[dict], default_work_days: float, default_work_hours: float) -> None:
        logging.debug("[LOAD] start: job_role_table")
        if self.table.state() == QAbstractItemView.State.EditingState:
            return
        self._loading = True
        self.table.setUpdatesEnabled(False)
        self.table.blockSignals(True)
        try:
            editor = self.table.focusWidget()
            if editor is not None and editor is not self.table:
                self.table.commitData(editor)
                self.table.closeEditor(editor, QAbstractItemDelegate.EndEditHint.SubmitModelCache)
            self._available_roles = roles
            self._role_name_map = {r["job_code"]: r["job_name"] for r in roles}
            job_mapping = get_job_mapping_from_file()
            self.table.setRowCount(0)
            for role in roles:
                row_idx = self.table.rowCount()
                self.table.insertRow(row_idx)
                job_code = role["job_code"]
                job_name = role["job_name"]
                grade = (job_mapping.get(job_code) or {}).get("grade", "") if isinstance(job_mapping.get(job_code), dict) else ""

                code_item = QTableWidgetItem(job_code)
                code_item.setFlags(self.EDITABLE_FLAGS)
                name_item = QTableWidgetItem(job_name)
                name_item.setFlags(self.READONLY_FLAGS)
                grade_item = QTableWidgetItem(grade)
                grade_item.setFlags(self.READONLY_FLAGS)

                self.table.setItem(row_idx, COL_JOB_CODE, code_item)
                self.table.setItem(row_idx, COL_JOB_NAME, name_item)
                self.table.setItem(row_idx, COL_GRADE, grade_item)

                # 근무일수·근무시간만 읽기 전용, 연장·휴일근로·인원은 수정 가능
                work_days_item = QTableWidgetItem(str(default_work_days))
                work_days_item.setFlags(self.READONLY_FLAGS)
                work_hours_item = QTableWidgetItem(str(default_work_hours))
                work_hours_item.setFlags(self.READONLY_FLAGS)
                overtime_item = QTableWidgetItem("0")
                overtime_item.setFlags(self.EDITABLE_FLAGS)
                holiday_item = QTableWidgetItem("0")
                holiday_item.setFlags(self.EDITABLE_FLAGS)
                headcount_item = QTableWidgetItem("0")
                headcount_item.setFlags(self.EDITABLE_FLAGS)

                self.table.setItem(row_idx, COL_WORK_DAYS, work_days_item)
                self.table.setItem(row_idx, COL_WORK_HOURS, work_hours_item)
                self.table.setItem(row_idx, COL_OVERTIME_HOURS, overtime_item)
                self.table.setItem(row_idx, COL_HOLIDAY_HOURS, holiday_item)
                self.table.setItem(row_idx, COL_HEADCOUNT, headcount_item)

                self.table._ensure_row_items(row_idx)
                self.table._set_job_name_readonly(row_idx)
                self.table._set_grade_readonly(row_idx)
                self._set_auto_columns_readonly_for_row(row_idx)
            self._force_editable()
        finally:
            self.table.blockSignals(False)
            self.table.setUpdatesEnabled(True)
            self._loading = False
            logging.debug("[LOAD] end: job_role_table")

    def set_job_inputs(self, job_inputs: dict[str, dict]) -> None:
        self._loading = True
        self.table.setUpdatesEnabled(False)
        self.table.blockSignals(True)
        try:
            for row in range(self.table.rowCount()):
                job_code = self._get_job_code(row)
                if job_code not in job_inputs:
                    continue  # 저장된 데이터 없는 직무는 기본값 유지
                values = job_inputs[job_code]
                self.table.item(row, COL_WORK_DAYS).setText(str(values.get("work_days", 0)))
                self.table.item(row, COL_WORK_HOURS).setText(str(values.get("work_hours", 0)))
                self.table.item(row, COL_OVERTIME_HOURS).setText(str(values.get("overtime_hours", 0)))
                self.table.item(row, COL_HOLIDAY_HOURS).setText(str(values.get("holiday_work_days", values.get("holiday_work_hours", 0))))
                hc = values.get("headcount", 0)
                self.table.item(row, COL_HEADCOUNT).setText(str(int(hc)) if isinstance(hc, float) and hc == int(hc) else str(hc))
            self._force_editable()
        finally:
            self.table.blockSignals(False)
            self.table.setUpdatesEnabled(True)
            self._loading = False

    def get_job_inputs(self) -> dict[str, dict]:
        self.table.setCurrentCell(-1, -1)
        editor = self.table.focusWidget()
        if editor is not None and editor is not self.table:
            self.table.commitData(editor)
            self.table.closeEditor(editor, QAbstractItemDelegate.EndEditHint.SubmitModelCache)
        result = {}
        for row in range(self.table.rowCount()):
            job_code = self._get_job_code(row)
            if not job_code:
                logging.debug("JobRoleTable: empty job_code at row=%s", row)
                continue

            def safe_get(col: int) -> str:
                item = self.table.item(row, col)
                return item.text().strip() if item and item.text() else "0"

            fallback = {
                "work_days": 0.0,
                "work_hours": 0.0,
                "overtime_hours": 0.0,
                "holiday_work_days": 0.0,
                "headcount": 0,
            }
            try:
                result[job_code] = {
                    "work_days": self._to_float(safe_get(COL_WORK_DAYS)),
                    "work_hours": self._to_float(safe_get(COL_WORK_HOURS)),
                    "overtime_hours": self._to_float(safe_get(COL_OVERTIME_HOURS)),
                    "holiday_work_days": self._to_float(safe_get(COL_HOLIDAY_HOURS)),
                    "headcount": self._to_int(safe_get(COL_HEADCOUNT)),
                }
            except Exception as exc:
                logging.warning("JobRoleTable: extract row %s failed, using fallback: %s", row, exc)
                result[job_code] = fallback

        logging.debug("JobRoleTable: total jobs extracted: %s", list(result.keys()))
        return result

    def on_change(self, callback) -> None:
        self._external_on_change = callback

    def _handle_item_changed(self, item) -> None:
        if self._loading:
            return
        if item.column() == COL_JOB_CODE:
            self._sync_name_grade_for_row(item.row())
        self.dirty = True
        if self._external_on_change:
            # Defer so delegate commit and model update are done before 노무비 상세 자동계산
            QTimer.singleShot(0, self._external_on_change)

    def _sync_name_grade_for_row(self, row: int) -> None:
        """직무코드 셀 변경 시 해당 행의 직무명·직종을 동기화 (시그널 차단하여 itemChanged 중복 방지)."""
        code = (self.table.item(row, COL_JOB_CODE).text() or "").strip() if self.table.item(row, COL_JOB_CODE) else ""
        name = self._role_name_map.get(code, "")
        job_mapping = get_job_mapping_from_file()
        meta = job_mapping.get(code) or {}
        grade = meta.get("grade", "") if isinstance(meta, dict) else ""
        self.table.blockSignals(True)
        try:
            name_item = self.table.item(row, COL_JOB_NAME)
            if name_item is None:
                name_item = QTableWidgetItem("")
                self.table.setItem(row, COL_JOB_NAME, name_item)
            name_item.setText(name)
            self.table._set_job_name_readonly(row)
            grade_item = self.table.item(row, COL_GRADE)
            if grade_item is None:
                grade_item = QTableWidgetItem("")
                self.table.setItem(row, COL_GRADE, grade_item)
            grade_item.setText(grade)
            self.table._set_grade_readonly(row)
        finally:
            self.table.blockSignals(False)

    def is_editing(self) -> bool:
        if self.table.state() == QAbstractItemView.State.EditingState:
            return True
        editor = self.table.focusWidget()
        return editor is not None and editor is not self.table

    def add_empty_row(self) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table._ensure_row_items(row)
        code_item = self.table.item(row, COL_JOB_CODE)
        if code_item is not None:
            code_item.setFlags(self.EDITABLE_FLAGS)
        self.table._set_job_name_readonly(row)
        self.table._set_grade_readonly(row)
        # 근무일수·근무시간만 읽기 전용, 연장·휴일근로·인원은 수정 가능
        self.table.setItem(row, COL_WORK_DAYS, QTableWidgetItem("22"))
        self.table.setItem(row, COL_WORK_HOURS, QTableWidgetItem("8"))
        overtime_item = QTableWidgetItem("0")
        overtime_item.setFlags(self.EDITABLE_FLAGS)
        self.table.setItem(row, COL_OVERTIME_HOURS, overtime_item)
        holiday_item = QTableWidgetItem("0")
        holiday_item.setFlags(self.EDITABLE_FLAGS)
        self.table.setItem(row, COL_HOLIDAY_HOURS, holiday_item)
        self._set_auto_columns_readonly_for_row(row)
        headcount_item = self.table.item(row, COL_HEADCOUNT)
        if headcount_item is not None:
            headcount_item.setFlags(self.EDITABLE_FLAGS)

    def set_available_roles(self, roles: list[dict]) -> None:
        self._available_roles = roles
        self._role_name_map = {r["job_code"]: r["job_name"] for r in roles}

    def _get_job_code(self, row: int) -> str:
        item = self.table.item(row, COL_JOB_CODE)
        return (item.text() or "").strip() if item is not None else ""

    def _to_float(self, text: str) -> float:
        if not text:
            return 0.0
        try:
            cleaned = re.sub(r"[^0-9.]", "", text)
            return float(cleaned) if cleaned else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _to_int(self, text: str) -> int:
        if not text:
            return 0
        try:
            cleaned = re.sub(r"[^0-9.]", "", text)
            return int(float(cleaned)) if cleaned else 0
        except (ValueError, TypeError):
            return 0

    def _set_auto_columns_readonly_for_row(self, row: int) -> None:
        """근무일수·근무시간만 읽기 전용. 연장·휴일근로는 수정 가능."""
        for col in (COL_WORK_DAYS, COL_WORK_HOURS):
            item = self.table.item(row, col)
            if item is not None:
                item.setFlags(self.READONLY_FLAGS)

    def _set_auto_columns_readonly(self) -> None:
        """모든 행에 대해 근무일수·근무시간만 읽기 전용으로 설정."""
        for row in range(self.table.rowCount()):
            self._set_auto_columns_readonly_for_row(row)

    def _force_editable(self) -> None:
        _force_editable_full(self.table, tag="JOB_TABLE")
        self._set_auto_columns_readonly()
        self._assert_editable()

    def _assert_editable(self) -> None:
        if self.table.columnCount() <= 0:
            raise RuntimeError("JobRoleTable: columnCount is 0")
        if self.table.rowCount() <= 0:
            raise RuntimeError("JobRoleTable: rowCount is 0")
        # 직무코드(0)·인원(7)만 편집 가능; 편집 가능 셀인 인원(7)로 검사
        item = self.table.item(0, COL_HEADCOUNT)
        if item is None:
            raise RuntimeError("JobRoleTable: item(0, COL_HEADCOUNT) is None")
        if not (item.flags() & Qt.ItemFlag.ItemIsEditable):
            raise RuntimeError("JobRoleTable: item(0, COL_HEADCOUNT) is not editable")
