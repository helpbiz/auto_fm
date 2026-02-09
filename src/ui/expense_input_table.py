import logging
import os
import traceback
from functools import partial

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QComboBox,
    QLineEdit,
    QStyledItemDelegate,
)
from PyQt6.QtCore import Qt, QTimer, QObject, QEvent
from PyQt6.QtGui import QDoubleValidator, QIntValidator

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
        logging.debug("%s.setEnabled(%s) called", name, val)
        return orig_set_enabled(val)

    def set_edit_triggers_hook(val):
        v_int = _to_int_safe(val)
        v_repr = repr(val)
        logging.warning(
            f"{name}.setEditTriggers(val={v_repr}, int={v_int}) called!"
        )
        return orig_set_edit_triggers(val)

    def vp_set_enabled_hook(val: bool):
        logging.debug("%s.viewport().setEnabled(%s) called", name, val)
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


class ExpenseInputTable(QWidget):
    """
    경비 입력 테이블 (표준 단가 읽기 전용)
    """

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self._loading = False
        self.dirty = False
        self._external_on_change = None
        self._available_items: list[dict] = []
        self._item_map: dict[str, dict] = {}

        title = QLabel("경비 입력")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)

        editable_flags = (
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsEditable
        )
        readonly_flags = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

        self.table = QTableWidget(0, 6)
        class IntegerDelegate(QStyledItemDelegate):
            def createEditor(self, parent, option, index):
                editor = QLineEdit(parent)
                editor.setValidator(QIntValidator(0, 100_000_000))
                return editor

        class FloatDelegate(QStyledItemDelegate):
            def createEditor(self, parent, option, index):
                editor = QLineEdit(parent)
                editor.setValidator(QDoubleValidator(0.0, 1_000_000.0, 4))
                return editor

        self.table.setItemDelegateForColumn(3, IntegerDelegate(self.table))
        self.table.setItemDelegateForColumn(5, FloatDelegate(self.table))
        self.table.setHorizontalHeaderLabels(
            ["경비코드", "항목명", "구분", "단가(표준)", "단위", "수량"]
        )
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.SelectedClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
            | QAbstractItemView.EditTrigger.AnyKeyPressed
        )
        self.table.setEnabled(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        attach_table_debug_hooks(self.table, name="exp_table")
        hook_suspicious_methods(self.table, name="exp_table")
        self.table.itemChanged.connect(self._handle_item_changed)
        self._force_editable()
        layout.addWidget(self.table)

    def load_items(self, items: list[dict], prices: dict[str, dict]) -> None:
        logging.debug("[LOAD] start: expense_input_table")
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
            self._available_items = items
            self._item_map = {
                i["exp_code"]: {
                    "exp_name": i["exp_name"],
                    "group_code": i["group_code"],
                    "unit_price": prices.get(i["exp_code"], {}).get("unit_price", 0),
                    "unit": prices.get(i["exp_code"], {}).get("unit", ""),
                }
                for i in items
            }
            self.table.setRowCount(0)
            sorted_items = sorted(
                items,
                key=lambda x: (x.get("group_code", ""), x.get("sort_order", 0), x.get("exp_code", "")),
            )
            for item in sorted_items:
                row_idx = self.table.rowCount()
                self.table.insertRow(row_idx)
                exp_code = item["exp_code"]
                exp_name = item["exp_name"]
                group_code = item["group_code"]

                price = prices.get(exp_code, {})
                unit_price = price.get("unit_price", 0)
                unit = price.get("unit", "")

                code_item = QTableWidgetItem(exp_code)
                code_item.setFlags(readonly_flags)
                name_item = QTableWidgetItem(exp_name)
                name_item.setFlags(readonly_flags)
                group_item = QTableWidgetItem(group_code)
                group_item.setFlags(readonly_flags)
                price_item = QTableWidgetItem(str(unit_price))
                price_item.setFlags(editable_flags)
                unit_item = QTableWidgetItem(unit)
                unit_item.setFlags(readonly_flags)

                self.table.setItem(row_idx, 0, code_item)
                self.table.setItem(row_idx, 1, name_item)
                self.table.setItem(row_idx, 2, group_item)
                self.table.setItem(row_idx, 3, price_item)
                self.table.setItem(row_idx, 4, unit_item)

                qty_item = QTableWidgetItem("0")
                qty_item.setFlags(editable_flags)
                self.table.setItem(row_idx, 5, qty_item)

                for col in range(self.table.columnCount()):
                    if self.table.item(row_idx, col) is None:
                        self.table.setItem(row_idx, col, QTableWidgetItem(""))
            self._force_editable()
        finally:
            self.table.blockSignals(False)
            self.table.setUpdatesEnabled(True)
            self._loading = False
            logging.debug("[LOAD] end: expense_input_table")

    def set_items(self, items: dict[str, dict]) -> None:
        self._loading = True
        self.table.setUpdatesEnabled(False)
        self.table.blockSignals(True)
        try:
            for row in range(self.table.rowCount()):
                exp_code = self.table.item(row, 0).text()
                values = items.get(exp_code, {})
                self.table.item(row, 3).setText(str(values.get("unit_price", 0)))
                self.table.item(row, 5).setText(str(values.get("quantity", 0)))
            self._force_editable()
        finally:
            self.table.blockSignals(False)
            self.table.setUpdatesEnabled(True)
            self._loading = False

    def get_items(self) -> dict[str, dict]:
        result = {}
        for row in range(self.table.rowCount()):
            exp_code = self.table.item(row, 0).text()
            qty_text = self.table.item(row, 5).text().strip()
            price_text = self.table.item(row, 3).text().strip()
            result[exp_code] = {
                "quantity": self._to_float(qty_text),
                "unit_price": self._to_int(price_text),
            }
        return result

    def on_change(self, callback) -> None:
        self._external_on_change = callback

    def _handle_item_changed(self, item) -> None:
        if self._loading:
            return
        self.dirty = True
        if self._external_on_change:
            self._external_on_change()

    def is_editing(self) -> bool:
        if self.table.state() == QAbstractItemView.State.EditingState:
            return True
        editor = self.table.focusWidget()
        return editor is not None and editor is not self.table

    def add_empty_row(self) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        for col in range(self.table.columnCount()):
            if self.table.item(row, col) is None:
                self.table.setItem(row, col, QTableWidgetItem(""))
        self._install_exp_code_combo(row, "")

    def set_available_items(self, items: list[dict], prices: dict[str, dict]) -> None:
        self._available_items = items
        self._item_map = {
            i["exp_code"]: {
                "exp_name": i["exp_name"],
                "group_code": i["group_code"],
                "unit_price": prices.get(i["exp_code"], {}).get("unit_price", 0),
                "unit": prices.get(i["exp_code"], {}).get("unit", ""),
            }
            for i in items
        }

    def _install_exp_code_combo(self, row: int, current_code: str) -> None:
        if not self._available_items:
            return
        combo = QComboBox(self.table)
        combo.addItem("")
        for item in self._available_items:
            combo.addItem(item["exp_code"])
        idx = combo.findText(current_code)
        combo.setCurrentIndex(idx if idx >= 0 else 0)
        combo.currentTextChanged.connect(partial(self._on_exp_code_changed, row))
        self.table.setCellWidget(row, 0, combo)
        if current_code:
            self._on_exp_code_changed(row, current_code)

    def _on_exp_code_changed(self, row: int, code: str) -> None:
        meta = self._item_map.get(code, {})
        self._set_text(row, 1, meta.get("exp_name", ""))
        self._set_text(row, 2, meta.get("group_code", ""))
        self._set_text(row, 3, str(meta.get("unit_price", 0)))
        self._set_text(row, 4, meta.get("unit", ""))
        for col in (1, 2, 4):
            item = self.table.item(row, col)
            if item is not None:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

    def _set_text(self, row: int, col: int, text: str) -> None:
        item = self.table.item(row, col)
        if item is None:
            item = QTableWidgetItem("")
            self.table.setItem(row, col, item)
        item.setText(text)

    def _int_editor(self, parent):
        editor = QLineEdit(parent)
        editor.setValidator(QIntValidator(0, 100_000_000))
        return editor

    def _float_editor(self, parent):
        editor = QLineEdit(parent)
        editor.setValidator(QDoubleValidator(0.0, 1_000_000.0, 4))
        return editor

    def _to_int(self, text: str) -> int:
        if not text:
            return 0
        try:
            return int(text.replace(",", ""))
        except ValueError:
            return 0

    def _to_float(self, text: str) -> float:
        if not text:
            return 0.0
        try:
            return float(text.replace(",", ""))
        except ValueError:
            return 0.0

    def _force_editable(self) -> None:
        _force_editable_full(self.table, tag="EXP_TABLE")
        self._assert_editable()

    def _assert_editable(self) -> None:
        if self.table.columnCount() <= 0:
            raise RuntimeError("ExpenseInputTable: columnCount is 0")
        if self.table.rowCount() <= 0:
            raise RuntimeError("ExpenseInputTable: rowCount is 0")
        item = self.table.item(0, 0)
        if item is None:
            raise RuntimeError("ExpenseInputTable: item(0,0) is None")
        if not (item.flags() & Qt.ItemFlag.ItemIsEditable):
            raise RuntimeError("ExpenseInputTable: item(0,0) is not editable")
