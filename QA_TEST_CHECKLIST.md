# QA Test Checklist - auto_fm v1.0

> 3개 Critical Fixes 검증을 위한 Zero Script QA 체크리스트

## 🎯 Test Environment

- **Date**: 2026-02-14
- **Version**: 1.0 (Post-Critical-Fix)
- **Tester**: _______________
- **OS**: Windows 11 Education 10.0.22631

---

## 🔧 Pre-Test Setup

### 1. Backup Current Logs

```powershell
cp logs\app.log logs\app.log.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')
```

### 2. Start Log Monitoring (별도 창)

```powershell
Get-Content -Path "logs\app.log" -Wait -Tail 50
```

### 3. Launch Application

```bash
python src/main.py
```

---

## ✅ Test Case 1: C-02 Settings 재귀 호출 방지

### Steps

- [ ] 1. 앱 실행 확인
- [ ] 2. 설정 다이얼로그 열기 (있는 경우)
- [ ] 3. 보험료율 중 하나 변경 (예: 산재보험 0.009 → 0.010)
- [ ] 4. 저장 버튼 클릭
- [ ] 5. 로그 확인: "config 저장 완료" 메시지 **1회만** 출력

### Expected Log

```json
{"level":"INFO","message":"config 저장 완료: C:\\Users\\helpbiz\\Documents\\auto_fm\\auto_fm\\data\\config.json"}
```

### Result

- [ ] ✅ PASS: 1회만 저장, 재귀 호출 없음
- [ ] ❌ FAIL: 2회 이상 저장 또는 RecursionError

**Notes**: _______________________________________________

---

## ✅ Test Case 2: H-02 비숫자 입력 처리

### Steps

- [ ] 1. 앱 메인 화면에서 "일반관리비율(%)" 필드 찾기
- [ ] 2. "abc" 입력
- [ ] 3. "이윤율(%)" 필드에 "xyz" 입력
- [ ] 4. 인원 데이터 입력 (예: "시설관리원 / 1명")
- [ ] 5. "집계 실행" 버튼 클릭
- [ ] 6. 앱 크래시 없이 계산 완료 확인
- [ ] 7. 로그 확인: ERROR 없이 기본값(18.5%, 15.0%) 사용

### Expected Behavior

- 앱이 크래시하지 않음
- 계산 결과에 기본값 적용 (일반관리비율: 18.5%, 이윤율: 15.0%)
- ValueError 로그 없음

### Expected Log

```json
{"level":"INFO","message":"계산 시작"}
{"level":"INFO","message":"계산 완료","data":{"overhead_rate":18.5,"profit_rate":15.0}}
```

### Result

- [ ] ✅ PASS: 기본값 사용, ERROR 없음
- [ ] ❌ FAIL: ValueError 발생 또는 크래시

**Actual Values Used**:
- 일반관리비율: _______%
- 이윤율: _______%

**Notes**: _______________________________________________

---

## ✅ Test Case 3: H-07 PDF 내보내기 (QColor import)

### Prerequisite

- 시나리오 2개 이상 필요 (없으면 생성)

### Steps

- [ ] 1. 시나리오 A 생성 및 저장 (예: "시나리오1")
- [ ] 2. 시나리오 B 생성 및 저장 (예: "시나리오2")
- [ ] 3. "비교" 탭 클릭
- [ ] 4. 좌측 시나리오 선택: "시나리오1"
- [ ] 5. 우측 시나리오 선택: "시나리오2"
- [ ] 6. "PDF 내보내기" 버튼 클릭
- [ ] 7. 파일 저장 다이얼로그에서 저장 위치 선택
- [ ] 8. PDF 파일 생성 확인
- [ ] 9. PDF 파일 열어서 내용 확인

### Expected Log

```json
{"level":"INFO","message":"PDF 내보내기 완료","data":{"file":"compare_결과.pdf"}}
```

### Result

- [ ] ✅ PASS: PDF 생성 성공, ERROR 없음
- [ ] ❌ FAIL: NameError 또는 PDF 생성 실패

**PDF File Path**: _______________________________________________

**Notes**: _______________________________________________

---

## 📊 Test Summary

### Overall Results

| Test Case | Status | Notes |
|-----------|--------|-------|
| C-02: Settings 재귀 방지 | ☐ PASS / ☐ FAIL | |
| H-02: 비숫자 입력 처리 | ☐ PASS / ☐ FAIL | |
| H-07: PDF QColor import | ☐ PASS / ☐ FAIL | |

### Pass Rate

- **Total Tests**: 3
- **Passed**: _____
- **Failed**: _____
- **Pass Rate**: _____%

### Production Readiness

- [ ] ✅ 100% Pass → Production 배포 가능
- [ ] ⚠️ 80-99% Pass → 마이너 이슈 수정 후 배포
- [ ] ❌ <80% Pass → 크리티컬 이슈 수정 필요

---

## 🐛 Issues Found

### Issue Template

```markdown
## ISSUE-00X: {이슈 제목}

- **Severity**: Critical / High / Medium / Low
- **Test Case**: TC-{번호}
- **Reproduction Steps**:
  1. ...
  2. ...
- **Log**:
  ```json
  {...}
  ```
- **Expected**: ...
- **Actual**: ...
- **Fix Suggestion**: ...
```

### Issues

*(여기에 발견된 이슈 기록)*

---

## 📝 Tester Sign-off

- **Tester Name**: _______________________________________________
- **Date**: _______________________________________________
- **Signature**: _______________________________________________
- **Overall Assessment**:
  - [ ] Ready for Production
  - [ ] Minor Fixes Required
  - [ ] Major Fixes Required

---

## 🔄 Next Steps

### If All Tests Pass (100%)

1. ✅ Update PDCA status: `/pdca report auto_fm`
2. ✅ Archive PDCA documents: `/pdca archive auto_fm`
3. ✅ Proceed to packaging: PyInstaller + Inno Setup

### If Issues Found (<100%)

1. ⚠️ Document all issues in this checklist
2. ⚠️ Run auto-improvement: `/pdca iterate auto_fm`
3. ⚠️ Re-test after fixes

---

## 📚 References

- [Zero Script QA Guide](docs/qa/zero-script-qa-guide.md)
- [PDCA Completion Report](docs/04-report/features/auto_fm.report.md)
- [Code Review Report](docs/03-analysis/code-review-2026-02-14.md)
