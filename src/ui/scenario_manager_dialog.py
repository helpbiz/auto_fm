"""
시나리오 관리 대화상자

저장된 모든 시나리오를 목록으로 표시하고,
선택한 시나리오를 삭제할 수 있습니다.
"""

import logging
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QMessageBox,
)
from PyQt6.QtCore import Qt

from src.domain.db import get_connection
from src.domain.scenario_input.service import list_scenario_ids, delete_scenario


class ScenarioManagerDialog(QDialog):
    """시나리오 관리 대화상자"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("시나리오 관리")
        self.setModal(True)
        self.resize(500, 400)
        self.deleted_scenarios = []  # 삭제된 시나리오 목록

        self._setup_ui()
        self._load_scenarios()

    def _setup_ui(self):
        """UI 구성"""
        layout = QVBoxLayout(self)

        # 안내 레이블
        info_label = QLabel("삭제할 시나리오를 선택하세요 (여러 개 선택 가능)")
        info_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(info_label)

        # 시나리오 목록
        self.scenario_list = QListWidget()
        self.scenario_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        layout.addWidget(self.scenario_list)

        # 정보 레이블
        self.count_label = QLabel("총 0개의 시나리오")
        layout.addWidget(self.count_label)

        # 버튼 영역
        button_layout = QHBoxLayout()

        self.refresh_button = QPushButton("새로고침")
        self.refresh_button.clicked.connect(self._load_scenarios)

        self.delete_button = QPushButton("선택 항목 삭제")
        self.delete_button.clicked.connect(self._delete_selected)
        self.delete_button.setStyleSheet("background-color: #d32f2f; color: white;")

        self.close_button = QPushButton("닫기")
        self.close_button.clicked.connect(self.accept)

        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def _load_scenarios(self):
        """데이터베이스에서 시나리오 목록 불러오기"""
        self.scenario_list.clear()

        try:
            conn = get_connection()
            try:
                scenario_ids = list_scenario_ids(conn)
            finally:
                conn.close()

            # default 시나리오 제외 (삭제 불가능)
            scenario_ids = [sid for sid in scenario_ids if sid.lower() != "default"]

            # 목록에 추가
            for scenario_id in scenario_ids:
                item = QListWidgetItem(scenario_id)
                self.scenario_list.addItem(item)

            # 카운트 업데이트
            self.count_label.setText(f"총 {len(scenario_ids)}개의 시나리오 (default 제외)")

            # 시나리오가 없으면 삭제 버튼 비활성화
            self.delete_button.setEnabled(len(scenario_ids) > 0)

        except Exception as e:
            logging.exception("시나리오 목록 로드 실패")
            QMessageBox.critical(
                self,
                "오류",
                f"시나리오 목록을 불러오는 중 오류가 발생했습니다.\n{e}"
            )

    def _delete_selected(self):
        """선택된 시나리오 삭제"""
        selected_items = self.scenario_list.selectedItems()

        if not selected_items:
            QMessageBox.information(
                self,
                "시나리오 삭제",
                "삭제할 시나리오를 선택하세요."
            )
            return

        # 선택된 시나리오 ID 추출
        scenario_ids = [item.text() for item in selected_items]

        # 확인 대화상자
        count = len(scenario_ids)
        scenario_names = "\n".join(f"  • {sid}" for sid in scenario_ids[:10])
        if count > 10:
            scenario_names += f"\n  ... 외 {count - 10}개"

        reply = QMessageBox.question(
            self,
            "시나리오 삭제 확인",
            f"다음 {count}개의 시나리오를 삭제하시겠습니까?\n\n"
            f"{scenario_names}\n\n"
            f"⚠️ 삭제된 시나리오의 모든 데이터가 영구적으로 제거됩니다.\n"
            f"이 작업은 되돌릴 수 없습니다.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # 삭제 수행
        success_count = 0
        failed_scenarios = []

        for scenario_id in scenario_ids:
            try:
                conn = get_connection()
                try:
                    delete_scenario(scenario_id, conn)
                    success_count += 1
                    self.deleted_scenarios.append(scenario_id)
                finally:
                    conn.close()
            except ValueError as e:
                # default 시나리오 등 삭제 불가능한 경우
                failed_scenarios.append((scenario_id, str(e)))
                logging.warning(f"시나리오 삭제 실패: {scenario_id} - {e}")
            except Exception as e:
                failed_scenarios.append((scenario_id, str(e)))
                logging.exception(f"시나리오 삭제 중 오류: {scenario_id}")

        # 목록 새로고침
        self._load_scenarios()

        # 결과 메시지
        if success_count > 0 and not failed_scenarios:
            QMessageBox.information(
                self,
                "삭제 완료",
                f"{success_count}개의 시나리오가 삭제되었습니다."
            )
        elif success_count > 0 and failed_scenarios:
            failed_list = "\n".join(f"  • {sid}: {err}" for sid, err in failed_scenarios[:5])
            if len(failed_scenarios) > 5:
                failed_list += f"\n  ... 외 {len(failed_scenarios) - 5}개"
            QMessageBox.warning(
                self,
                "일부 삭제 실패",
                f"{success_count}개 삭제 성공, {len(failed_scenarios)}개 실패\n\n"
                f"실패한 시나리오:\n{failed_list}"
            )
        else:
            failed_list = "\n".join(f"  • {sid}: {err}" for sid, err in failed_scenarios[:5])
            if len(failed_scenarios) > 5:
                failed_list += f"\n  ... 외 {len(failed_scenarios) - 5}개"
            QMessageBox.critical(
                self,
                "삭제 실패",
                f"시나리오 삭제에 실패했습니다.\n\n{failed_list}"
            )

    def get_deleted_scenarios(self):
        """삭제된 시나리오 ID 목록 반환"""
        return self.deleted_scenarios
