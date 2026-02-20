# DB 오류 분석 리포트

**분석 일시**: 2026-02-14
**DB 경로**: `C:\Users\helpbiz\AppData\Local\auto_fm\app.db`

---

## 발견된 오류 요약

| 시나리오 | 오류 내용 | Severity |
|---------|----------|----------|
| **시나리오1** | overhead_rate: None | **Critical** |
| **시나리오1** | profit_rate: None | **Critical** |
| **시나리오1** | Job names: None | Medium |
| **시나리오3** | overhead_rate: None | **Critical** |
| **시나리오3** | profit_rate: None | **Critical** |
| **시나리오3** | 인원 데이터 없음 (0명) | **High** |

---

## 시나리오1 상세

### 저장된 데이터
```json
{
  "overhead_rate": null,  // ❌ CRITICAL ERROR
  "profit_rate": null,    // ❌ CRITICAL ERROR
  "labor": {
    "job_roles": {
      "job1": {
        "job_name": null,  // ⚠️ Warning
        "headcount": 1.0
      },
      "job2": {
        "job_name": null,  // ⚠️ Warning
        "headcount": 1.0
      }
    }
  }
}
```

### 통계
- ✅ 총 직무: 2개
- ✅ 총 인원: 2명
- ✅ 집계 결과 있음: **26,905,276원**
- ❌ overhead_rate: **None** (예상: 10% 또는 18.5%)
- ❌ profit_rate: **None** (예상: 10% 또는 15.0%)

### 영향
계산 결과가 26,905,276원으로 나왔으나, overhead_rate와 profit_rate가 None이므로:
- 일반관리비와 이윤이 **0으로 계산**되었거나
- 시스템 기본값으로 계산되었을 가능성
- **결과 신뢰도 낮음**

---

## 시나리오3 상세

### 저장된 데이터
```json
{
  "overhead_rate": null,  // ❌ CRITICAL ERROR
  "profit_rate": null,    // ❌ CRITICAL ERROR
  "labor": {
    "job_roles": {}  // ❌ EMPTY - 인원 데이터 없음
  }
}
```

### 통계
- ❌ 총 직무: 0개
- ❌ 총 인원: 0명
- ✅ 집계 결과 있음: **53,208,326원**
- ❌ overhead_rate: **None**
- ❌ profit_rate: **None**

### 영향
**심각한 데이터 불일치**:
- 인원 데이터가 **0명**인데
- 집계 결과가 **53,208,326원**으로 존재
- 이것은 **논리적으로 불가능**
- **데이터 무결성 문제 발생**

---

## 근본 원인 분석

### 원인 1: ISSUE-006 (이미 수정)
**문제**: 입력 검증 없이 집계 실행 시 None 값 저장

**발생 시나리오**:
1. 일반관리비율/이윤율 필드 비워둠
2. "집계 실행" 클릭
3. DB에 None 저장
4. 인원 데이터 손실 (또는 저장 안됨)

**수정 완료**:
- [main_window.py:344-397](main_window.py#L344-L397)
- 사전 입력 검증 추가
- 명확한 오류 메시지 표시
- 데이터 손실 방지

### 원인 2: Job Metadata 누락
**문제**: job_name이 None으로 저장됨

**추정 원인**:
- 마스터 데이터 (md_job_role) 동기화 실패
- Seed 데이터 미적용

---

## 권장 조치

### 즉시 조치 (Critical)

#### 1. 시나리오1 수정
```sql
UPDATE scenario_input
SET input_json = json_set(
    input_json,
    '$.overhead_rate', 10.0,
    '$.profit_rate', 10.0
)
WHERE scenario_id = '시나리오1';
```

#### 2. 시나리오3 삭제 또는 재생성
```sql
-- Option A: 삭제
DELETE FROM scenario_input WHERE scenario_id = '시나리오3';
DELETE FROM calculation_result WHERE scenario_id = '시나리오3';

-- Option B: 재생성 필요 (GUI에서)
```

### 중기 조치 (High)

#### 3. DB 무결성 제약조건 추가
```sql
-- 향후 migration에 추가
CREATE TABLE scenario_input_v2 (
  scenario_id TEXT PRIMARY KEY,
  input_json TEXT NOT NULL,
  overhead_rate REAL NOT NULL DEFAULT 10.0,  -- 별도 컬럼으로 관리
  profit_rate REAL NOT NULL DEFAULT 10.0,    -- 별도 컬럼으로 관리
  updated_at TEXT NOT NULL,
  CHECK(overhead_rate >= 0 AND overhead_rate <= 100),
  CHECK(profit_rate >= 0 AND profit_rate <= 100)
);
```

### 장기 조치 (Medium)

#### 4. 데이터 검증 레이어 추가
- DB 저장 전 Validation
- None 값 자동 방어
- 기본값 강제 적용

#### 5. GUI 필드 기본값 설정
- 현재: "10" (수정됨)
- 빈 필드 허용 안함

---

## 테스트 권장사항

### 재생성 테스트
1. 시나리오3 삭제
2. 새로 생성:
   - 시나리오명: "시나리오3"
   - 일반관리비율: **10%** (필수 입력)
   - 이윤율: **10%** (필수 입력)
   - 인원 데이터: 최소 1명 이상
3. "집계 실행"
4. DB 확인

### 검증 쿼리
```sql
-- overhead/profit가 None인 시나리오 찾기
SELECT scenario_id,
       json_extract(input_json, '$.overhead_rate') as overhead,
       json_extract(input_json, '$.profit_rate') as profit
FROM scenario_input
WHERE json_extract(input_json, '$.overhead_rate') IS NULL
   OR json_extract(input_json, '$.profit_rate') IS NULL;

-- 인원 0명인데 집계 결과 있는 시나리오 찾기 (논리 오류)
SELECT si.scenario_id,
       json_extract(si.input_json, '$.labor.job_roles') as jobs,
       cr.result_json
FROM scenario_input si
LEFT JOIN calculation_result cr ON si.scenario_id = cr.scenario_id
WHERE json_extract(si.input_json, '$.labor.job_roles') = '{}'
  AND cr.scenario_id IS NOT NULL;
```

---

## 결론

**현재 상태**: ❌ **배포 불가**

**이유**:
1. Critical 데이터 오류 (overhead/profit = None)
2. 데이터 무결성 문제 (인원 0명인데 계산 결과 존재)
3. 사용자 혼란 가능성 높음

**다음 단계**:
1. ✅ ISSUE-006 수정 완료 (입력 검증 추가)
2. ⏳ 기존 데이터 정리 필요
3. ⏳ 재테스트 필요
4. ⏳ QA Report 작성

**예상 소요 시간**: 30분 (데이터 정리 + 재테스트)
