"""연도 로드 기능 테스트"""
import sys
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("1. 경로 테스트")
print("=" * 70)

from pathlib import Path
import json

current_file = Path(__file__)
project_root = current_file.parent
wages_json = project_root / "data" / "wages_master.json"

print(f"현재 파일: {current_file}")
print(f"프로젝트 루트: {project_root}")
print(f"wages_master.json 경로: {wages_json}")
print(f"파일 존재 여부: {wages_json.exists()}")

if wages_json.exists():
    print("\n" + "=" * 70)
    print("2. JSON 로드 테스트")
    print("=" * 70)

    with open(wages_json, 'r', encoding='utf-8') as f:
        wages_master = json.load(f)

    print(f"로드된 데이터: {wages_master}")

    years = sorted(wages_master.keys(), reverse=True)
    print(f"정렬된 연도 목록: {years}")
    print(f"연도 개수: {len(years)}")
else:
    print("ERROR: wages_master.json 파일이 없습니다!")

print("\n" + "=" * 70)
print("3. InputPanel 테스트")
print("=" * 70)

try:
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)

    from src.ui.input_panel import InputPanel

    panel = InputPanel()
    print(f"InputPanel 생성 완료")
    print(f"year_combo 아이템 개수: {panel.year_combo.count()}")

    for i in range(panel.year_combo.count()):
        print(f"  - 아이템 {i}: {panel.year_combo.itemText(i)}")

except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    print(traceback.format_exc())

print("\n테스트 완료!")
