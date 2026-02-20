# Zero Script QA Guide - auto_fm Desktop App

> 테스트 스크립트 없이 구조화 로그와 수동 테스트로 품질을 검증하는 방법론

## 📋 Overview

Zero Script QA는 웹 서비스를 위해 설계되었지만, 데스크톱 앱에도 적용 가능합니다.

### Desktop App 적용 방식

| 웹 서비스 | 데스크톱 앱 (auto_fm) |
|----------|---------------------|
| Docker logs 모니터링 | logs/app.log tail 모니터링 |
| Request ID 추적 | Session ID / Scenario ID 추적 |
| API 응답 시간 측정 | UI 작업 소요 시간 측정 |
| HTTP status 검증 | Exception 여부 검증 |
| JSON 로그 | JSON 로그 (업그레이드 완료) |

## 🔧 Logging Infrastructure

### JSON Format Example

```json
{
  "timestamp": "2026-02-14T15:30:45.123456",
  "level": "INFO",
  "service": "auto_fm",
  "message": "계산 완료",
  "data": {
    "scenario_id": "시나리오1",
    "labor_total": 1500000,
    "overhead_rate": 18.5,
    "profit_rate": 15.0,
    "duration_ms": 125
  }
}
```

### Log Levels

| Level | 용도 | 예시 |
|-------|-----|------|
| DEBUG | 상세 디버깅 정보 | 계산 중간값, 변수 상태 |
| INFO | 정상 작업 흐름 | 계산 시작/완료, 시나리오 저장 |
| WARNING | 주의가 필요한 상황 | 비정상 입력값, 기본값 사용 |
| ERROR | 에러 발생 | DB 오류, 계산 실패 |

## 📝 Critical Fixes QA Test Plan

### 수정 사항 요약

1. **C-02**: settings_manager.py 재귀 호출 위험 수정
2. **H-02**: input_panel.py 비숫자 입력 처리 개선
3. **H-07**: compare_page.py QColor import 누락 수정

### Test Case 1: C-02 - Settings 저장/로드 안정성

**목적**: settings_manager 재귀 호출 방지 검증

**테스트 순서**:
1. 앱 실행
2. 설정 다이얼로그 열기 (존재하는 경우)
3. 보험료율 변경 후 저장
4. 앱 재시작
5. 설정값 유지 확인

**로그 확인 포인트**:
```json
// 정상: 재귀 호출 없이 1번만 저장
{"level":"INFO","message":"config 저장 완료: ..."}

// 비정상: 재귀 호출 발생 (2회 이상 연속 저장)
{"level":"INFO","message":"config 저장 완료: ..."}
{"level":"INFO","message":"config 저장 완료: ..."}  // ❌ 재귀!
```

**판정 기준**:
- ✅ PASS: 설정 저장 시 1회만 로그 출력
- ❌ FAIL: 설정 저장 시 2회 이상 연속 로그 출력 (재귀 호출)

---

### Test Case 2: H-02 - 비숫자 입력 처리

**목적**: 일반관리비율/이윤율 필드 비정상 입력 방어 검증

**테스트 순서**:
1. 앱 실행
2. 일반관리비율 필드에 "abc" 입력
3. 이윤율 필드에 "xyz" 입력
4. 인원 데이터 입력
5. "집계 실행" 버튼 클릭
6. 앱이 크래시 없이 계산 완료 확인
7. 결과에서 기본값(18.5%, 15.0%) 적용 확인

**로그 확인 포인트**:
```json
// 정상: ValueError 없이 기본값 사용
{"level":"INFO","message":"계산 시작","data":{"overhead_rate":18.5,"profit_rate":15.0}}

// 비정상: ValueError 발생 (수정 전)
{"level":"ERROR","message":"could not convert string to float: 'abc'"}
```

**판정 기준**:
- ✅ PASS: 비숫자 입력 시 기본값(18.5%, 15.0%) 사용, ERROR 로그 없음
- ❌ FAIL: ValueError 발생 또는 앱 크래시

---

### Test Case 3: H-07 - 비교 결과 PDF 내보내기

**목적**: QColor import 누락으로 인한 PDF 내보내기 실패 방지 검증

**테스트 순서**:
1. 앱 실행
2. 시나리오 2개 이상 생성 (또는 로드)
3. "비교" 탭으로 이동
4. 시나리오 2개 선택
5. "PDF 내보내기" 버튼 클릭
6. PDF 생성 성공 확인

**로그 확인 포인트**:
```json
// 정상: PDF 생성 성공
{"level":"INFO","message":"PDF 내보내기 완료","data":{"file":"compare_결과.pdf"}}

// 비정상: QColor import 누락 (수정 전)
{"level":"ERROR","message":"NameError: name 'QColor' is not defined"}
```

**판정 기준**:
- ✅ PASS: PDF 생성 성공, ERROR 로그 없음
- ❌ FAIL: NameError 또는 PDF 생성 실패

---

## 🔍 Real-time Log Monitoring (Windows)

### PowerShell에서 로그 모니터링

```powershell
# logs/app.log 실시간 감시
Get-Content -Path "logs\app.log" -Wait -Tail 50
```

### Git Bash / WSL에서 로그 모니터링

```bash
# Unix-style tail
tail -f logs/app.log
```

### 로그 필터링 (특정 레벨만 보기)

```powershell
# ERROR 로그만 필터링
Get-Content -Path "logs\app.log" -Wait -Tail 50 | Select-String -Pattern '"level":"ERROR"'
```

---

## 📊 Log Analysis Checklist

실시간 로그를 보면서 다음 패턴을 확인:

### ✅ 정상 패턴

```json
{"level":"INFO","message":"계산 시작"}
{"level":"INFO","message":"노무비 계산 완료","data":{"labor_total":1500000}}
{"level":"INFO","message":"일반관리비 계산","data":{"overhead_rate":18.5,"overhead_cost":277500}}
{"level":"INFO","message":"이윤 계산","data":{"profit_rate":15.0,"profit":266625}}
{"level":"INFO","message":"계산 완료","data":{"total":2044125}}
```

### ❌ 비정상 패턴

```json
// 1. 연속된 에러 (3회 이상)
{"level":"ERROR","message":"DB 연결 실패"}
{"level":"ERROR","message":"DB 연결 실패"}
{"level":"ERROR","message":"DB 연결 실패"}

// 2. ValueError / TypeError
{"level":"ERROR","message":"could not convert string to float"}

// 3. NameError (import 누락)
{"level":"ERROR","message":"name 'QColor' is not defined"}

// 4. RecursionError (재귀 호출 오류)
{"level":"ERROR","message":"maximum recursion depth exceeded"}
```

---

## 🎯 QA Execution Steps

### 1단계: 로그 모니터링 시작

```powershell
# 새 PowerShell 창 열고 실시간 모니터링
cd C:\Users\helpbiz\Documents\auto_fm\auto_fm
Get-Content -Path "logs\app.log" -Wait -Tail 50
```

### 2단계: 앱 실행 및 테스트

```bash
# 기존 로그 백업 (선택)
cp logs/app.log logs/app.log.bak

# 새 로그로 시작 (선택)
echo "" > logs/app.log

# 앱 실행
python src/main.py
```

### 3단계: Test Cases 순차 실행

1. Test Case 1 실행 → 로그 확인
2. Test Case 2 실행 → 로그 확인
3. Test Case 3 실행 → 로그 확인

### 4단계: 이슈 문서화

발견된 이슈는 다음 형식으로 기록:

```markdown
## ISSUE-001: 설정 저장 시 중복 로그

- **Severity**: Medium
- **Reproduction**: 설정 다이얼로그 → 값 변경 → 저장
- **Log**:
  ```json
  {"level":"INFO","message":"config 저장 완료"}
  {"level":"INFO","message":"config 저장 완료"}
  ```
- **Problem**: save() 함수가 2회 호출됨
- **Fix**: 호출 경로 확인 필요
```

---

## 🚀 Next Steps After QA

### Pass Rate 계산

```
Pass Rate = (통과한 테스트 케이스 / 전체 테스트 케이스) × 100
```

| Pass Rate | Action |
|-----------|--------|
| 100% | ✅ Production 배포 가능 |
| 80-99% | ⚠️ 마이너 이슈 수정 후 배포 |
| <80% | ❌ 크리티컬 이슈 수정 필요 |

### PDCA Integration

- **Check 완료**: 3개 Test Cases 실행 완료
- **Act 필요**: Pass Rate < 100% 시 pdca-iterator로 자동 개선

```bash
# 이슈 발견 시
/pdca iterate auto_fm
```

---

## 📚 References

- [Zero Script QA Methodology](../../skills/zero-script-qa/README.md)
- [PDCA Analysis Report](../03-analysis/auto_fm.analysis.md)
- [Code Review Report](../03-analysis/code-review-2026-02-14.md)
