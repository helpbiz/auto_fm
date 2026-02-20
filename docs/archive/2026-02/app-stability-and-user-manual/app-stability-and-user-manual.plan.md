# Plan: App Stability & User Manual

> **Feature ID**: app-stability-and-user-manual
> **Created**: 2026-02-14
> **Status**: Planning
> **Priority**: High
> **Assignee**: Development Team

---

## 📋 Overview

### Goal
1. **에러 해결**: `python -m src.main` 실행 시 발생하는 모든 오류를 찾아 수정
2. **사용자 매뉴얼 작성**: 최종 사용자를 위한 포괄적인 사용 가이드 생성

### Background
원가산정 집계 시스템(auto_fm)이 개발되어 있지만:
- 실행 시 일부 오류가 발생할 가능성
- 사용자 문서가 부재하여 일반 사용자가 활용하기 어려움
- 체계적인 품질 검증 필요

### Success Criteria
- [x] 앱이 에러 없이 정상 실행됨
- [ ] 모든 핵심 기능이 정상 동작함
- [ ] 사용자 매뉴얼이 작성됨 (한글)
- [ ] 매뉴얼에 스크린샷 포함
- [ ] 설치/실행 가이드 포함

---

## 🎯 Requirements

### FR-01: 앱 실행 에러 진단 및 수정
**Description**: `python -m src.main` 실행 시 발생하는 모든 에러를 찾아 수정

**Acceptance Criteria**:
- Python 모듈 import 에러 없음
- PyQt6 UI 초기화 에러 없음
- 데이터베이스 연결 에러 없음
- 마스터 데이터 로딩 에러 없음
- 모든 탭이 정상 로드됨

**Priority**: P0 (Critical)

### FR-02: 핵심 기능 검증
**Description**: 앱의 모든 핵심 기능이 정상 동작하는지 확인

**Acceptance Criteria**:
- 직무별 인원입력 테이블 정상 동작
- 경비 입력 테이블 정상 동작
- 집계 실행 버튼 정상 동작
- 결과 계산 및 표시 정상
- 시나리오 저장/불러오기 정상
- 시나리오 비교 기능 정상

**Priority**: P0 (Critical)

### FR-03: 사용자 매뉴얼 작성 (한글)
**Description**: 일반 사용자가 앱을 쉽게 사용할 수 있도록 포괄적인 매뉴얼 작성

**Acceptance Criteria**:
- 목차 구조 명확
- 각 기능별 사용법 설명
- 스크린샷 포함 (주요 화면)
- 예제 시나리오 포함
- FAQ 섹션 포함

**Priority**: P0 (Critical)

**Content Structure**:
```
1. 시작하기
   - 시스템 요구사항
   - 설치 방법
   - 첫 실행

2. 기본 사용법
   - 화면 구성 소개
   - 기준년도 설정
   - 시나리오 생성

3. 직무별 인원 입력
   - 직무 선택 방법
   - 인원 수 입력
   - 근무일수/시간 설정

4. 경비 입력
   - 경비 항목 선택
   - 단가/수량 입력
   - 그룹별 분류

5. 집계 및 결과 확인
   - 집계 실행
   - 결과 해석
   - 상세 내역 확인

6. 시나리오 관리
   - 시나리오 저장
   - 시나리오 불러오기
   - 시나리오 비교

7. 데이터 내보내기
   - PDF 내보내기
   - Excel 내보내기
   - JSON 내보내기

8. 문제 해결
   - 자주 묻는 질문 (FAQ)
   - 오류 발생 시 대처법
   - 지원 연락처
```

**Priority**: P0 (Critical)

### FR-04: 설치/배포 가이드
**Description**: 개발자 및 관리자를 위한 설치 및 배포 문서

**Acceptance Criteria**:
- Python 환경 설정 가이드
- 의존성 패키지 설치 방법
- 데이터베이스 초기화 방법
- exe 빌드 방법 (PyInstaller)
- 배포 체크리스트

**Priority**: P1 (High)

---

## 🔍 Technical Analysis

### Current State
```
✅ 완료된 작업:
- PyQt6 기반 GUI 구현
- SQLite 데이터베이스 구조
- 인건비 계산 로직
- 경비 계산 로직
- 시나리오 비교 기능
- JSON 저장/불러오기

⚠️  확인 필요:
- 앱 실행 시 오류 여부
- 모든 기능 통합 테스트
- 사용자 문서 부재
```

### Dependencies
```python
# 필수 패키지 (requirements.txt 확인)
PyQt6>=6.0.0
Pillow>=10.0.0
reportlab>=4.0.0
openpyxl>=3.0.0
```

### Known Issues
- ~~보험요율 입력 필드 미사용 (이미 수정됨)~~
- ~~ComboBox 드롭다운 미표시 (이미 수정됨)~~
- ~~Dirty flag 초기화 문제 (이미 수정됨)~~
- 실행 시 추가 오류 확인 필요

---

## 📅 Implementation Plan

### Phase 1: 에러 진단 및 수정 (2-3 hours)
**Tasks**:
1. `python -m src.main` 실행 및 로그 수집
2. 모든 import 에러 확인 및 수정
3. PyQt6 초기화 에러 확인 및 수정
4. 데이터베이스 마이그레이션 에러 확인
5. 마스터 데이터 로딩 검증
6. 모든 탭 초기화 검증
7. 에러 없이 실행 확인

**Deliverables**:
- 수정된 소스 코드
- 에러 수정 로그
- 실행 확인 스크린샷

### Phase 2: 기능 검증 및 통합 테스트 (2-3 hours)
**Tasks**:
1. 직무별 인원입력 기능 테스트
2. 경비 입력 기능 테스트
3. 집계 실행 테스트
4. 결과 표시 테스트
5. 시나리오 저장/불러오기 테스트
6. 시나리오 비교 테스트
7. 내보내기 기능 테스트 (PDF, Excel)

**Deliverables**:
- 테스트 결과 보고서
- 발견된 버그 목록
- 수정 완료 확인

### Phase 3: 사용자 매뉴얼 작성 (4-5 hours)
**Tasks**:
1. 매뉴얼 구조 설계
2. 각 섹션별 내용 작성
3. 스크린샷 캡처 및 편집
4. 예제 시나리오 작성
5. FAQ 작성
6. 리뷰 및 수정

**Deliverables**:
- `USER_GUIDE.md` (한글 사용자 매뉴얼)
- 스크린샷 이미지 폴더
- 예제 데이터 파일

### Phase 4: 설치/배포 가이드 작성 (1-2 hours)
**Tasks**:
1. 개발 환경 설정 가이드 작성
2. 의존성 설치 방법 문서화
3. exe 빌드 스크립트 작성
4. 배포 체크리스트 작성

**Deliverables**:
- `INSTALL.md` (설치 가이드)
- `DEPLOY.md` (배포 가이드)
- `build.bat` 또는 `build.sh` 스크립트

---

## 🎨 User Stories

### US-01: 일반 사용자의 앱 실행
```
As a 일반 사용자
I want to 앱을 에러 없이 실행하고 싶다
So that 원가 계산을 시작할 수 있다
```

### US-02: 사용자의 기능 학습
```
As a 초보 사용자
I want to 각 기능의 사용법을 매뉴얼로 확인하고 싶다
So that 앱을 효과적으로 활용할 수 있다
```

### US-03: 관리자의 앱 배포
```
As a 시스템 관리자
I want to 앱을 다른 PC에 설치하고 싶다
So that 여러 사용자가 사용할 수 있도록 하고 싶다
```

---

## 🚀 Risks & Mitigation

### Risk 1: 숨겨진 에러 발견
**Impact**: High
**Probability**: Medium
**Mitigation**:
- 체계적인 테스트 시나리오 작성
- 각 기능별 단위 테스트 수행
- 통합 테스트 수행

### Risk 2: 문서 작성 시간 초과
**Impact**: Medium
**Probability**: Low
**Mitigation**:
- 문서 템플릿 활용
- 스크린샷 자동화 도구 사용
- 우선순위가 높은 섹션부터 작성

### Risk 3: 환경 의존성 문제
**Impact**: Medium
**Probability**: Medium
**Mitigation**:
- requirements.txt 정확히 관리
- Python 버전 명시
- 가상환경 사용 권장

---

## 📊 Metrics

### Success Metrics
- **에러율**: 0% (앱 실행 시 에러 없음)
- **기능 테스트 통과율**: 100%
- **문서 완성도**: 모든 섹션 작성 완료
- **스크린샷 포함**: 최소 15개 이상

### Quality Metrics
- **코드 품질**: 모든 에러 수정
- **문서 가독성**: 초보자도 이해 가능
- **예제 완성도**: 실제 사용 가능한 예제 포함

---

## 🔗 Dependencies

### External Dependencies
- Python 3.12+
- PyQt6
- SQLite
- reportlab (PDF)
- openpyxl (Excel)

### Internal Dependencies
- 기존 구현된 모든 모듈
- 데이터베이스 스키마
- 마스터 데이터

---

## 📝 Notes

### 중요 고려사항
1. 사용자 매뉴얼은 **비개발자**를 대상으로 작성
2. 스크린샷은 **실제 데이터**가 아닌 예제 데이터 사용
3. 문서는 **한글**로 작성 (개발자 문서는 영문 병기 가능)
4. 에러 수정 시 **기존 기능 영향도** 확인 필수

### Next Steps
1. 에러 진단 실행
2. Design 문서 작성 (`/pdca design app-stability-and-user-manual`)
3. 구현 시작

---

**Plan approved by**: Development Team
**Review date**: 2026-02-14
**Target completion**: 2026-02-15
