#!/usr/bin/env python
"""DB 오류 수정 스크립트"""

import sqlite3
import json
from src.domain.db import get_db_path

def fix_scenario(scenario_id: str):
    """시나리오 overhead/profit None 값을 10으로 수정"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute('SELECT input_json FROM scenario_input WHERE scenario_id = ?', (scenario_id,))
    row = cursor.fetchone()

    if not row:
        print(f'[SKIP] {scenario_id} 없음')
        conn.close()
        return

    data = json.loads(row[0])
    overhead = data.get('overhead_rate')
    profit = data.get('profit_rate')

    if overhead is None or profit is None:
        data['overhead_rate'] = 10.0
        data['profit_rate'] = 10.0

        cursor.execute(
            'UPDATE scenario_input SET input_json = ?, updated_at = datetime("now") WHERE scenario_id = ?',
            (json.dumps(data, ensure_ascii=False), scenario_id)
        )
        conn.commit()
        print(f'[OK] {scenario_id} 수정 완료 (overhead: 10%, profit: 10%)')
    else:
        print(f'[SKIP] {scenario_id} 이미 정상 (overhead: {overhead}%, profit: {profit}%)')

    conn.close()

def delete_invalid_scenario(scenario_id: str):
    """데이터 무결성 위반 시나리오 삭제"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute('DELETE FROM scenario_input WHERE scenario_id = ?', (scenario_id,))
    cursor.execute('DELETE FROM calculation_result WHERE scenario_id = ?', (scenario_id,))

    conn.commit()
    conn.close()
    print(f'[OK] {scenario_id} 삭제 완료 (재생성 필요)')

if __name__ == '__main__':
    print('=== DB 오류 수정 시작 ===\n')

    # 모든 시나리오의 None 값 수정
    fix_scenario('시나리오')
    fix_scenario('시나리오1')
    fix_scenario('시나리오2')
    fix_scenario('시나리오4')

    # 데이터 무결성 위반 시나리오 삭제 (0명 인원에 노무비 발생)
    delete_invalid_scenario('시나리오3')
    delete_invalid_scenario('시나리오4')

    print('\n=== 완료! ===')
    print('\n다음 단계:')
    print('  1. 앱 재시작')
    print('  2. 시나리오 불러오기 테스트')
    print('  3. 삭제된 시나리오 재생성 시 인원 데이터 입력 필수')
