# Auto FM 빌드 가이드

Windows용 독립 실행 파일(.exe) 및 인스톨러 생성 가이드입니다.

---

## 📋 필수 준비 사항

### 1. Python 환경
- **Python 3.8 이상** 설치 필요
- 현재 프로젝트: Python 3.12

### 2. 필수 도구 설치

#### PyInstaller (실행 파일 생성)
```bash
pip install pyinstaller
```

#### Inno Setup (인스톨러 생성)
- **다운로드:** https://jrsoftware.org/isdl.php
- **설치 위치:** `C:\Program Files (x86)\Inno Setup 6\`
- 한국어 지원

### 3. 프로젝트 의존성 설치
```bash
pip install -r requirements.txt
```

필수 패키지:
- PyQt6 >= 6.4.0
- openpyxl >= 3.0.0

---

## 🔨 빌드 과정

### 단계 1: 소스 코드 테스트

먼저 애플리케이션이 정상 동작하는지 확인:

```bash
python src/main.py
```

**확인 사항:**
- GUI 창이 정상적으로 열리는가?
- 노무비/경비 입력이 가능한가?
- 일반관리비/이윤 계산이 정상인가? (10% 캡 적용)
- PDF/Excel 내보내기가 동작하는가?

### 단계 2: 실행 파일 빌드

**방법 1: 배치 스크립트 사용 (권장)**
```bash
build.bat
```

**방법 2: 수동 빌드**
```bash
pyinstaller auto_fm.spec --clean --noconfirm
```

**출력:**
- `dist/AutoFM.exe` - 독립 실행 파일

**예상 파일 크기:** 50-100 MB (UPX 압축 적용 시)

**테스트:**
```bash
dist\AutoFM.exe
```

### 단계 3: 인스톨러 생성

**전제 조건:**
- `dist/AutoFM.exe` 파일이 존재해야 함
- Inno Setup 6 설치 완료

**방법 1: 배치 스크립트 사용 (권장)**
```bash
build_installer.bat
```

**방법 2: 수동 빌드**
```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

**출력:**
- `installer_output/AutoFM_Setup_v1.0.0.exe` - Windows 인스톨러

**인스톨러 기능:**
- 자동 설치 경로: `C:\Program Files\Auto FM\`
- 시작 메뉴 그룹 생성
- 바탕화면 바로가기 (선택 사항)
- 제어판 제거 프로그램 등록
- 한국어 인터페이스

---

## ✅ 테스트 체크리스트

### 로컬 테스트 (개발 PC)

- [ ] **소스 실행 테스트**
  - `python src/main.py` 정상 실행
  - 모든 기능 동작 확인

- [ ] **EXE 실행 테스트**
  - `dist\AutoFM.exe` 직접 실행
  - 데이터베이스 생성 확인 (`%LOCALAPPDATA%\auto_fm\app.db`)
  - 한글 입출력 정상 동작
  - PDF/Excel 내보내기 테스트

### 클린 머신 테스트 (Python 미설치 PC)

- [ ] **인스톨러 테스트**
  - `AutoFM_Setup_v1.0.0.exe` 실행
  - 설치 과정 완료
  - 시작 메뉴에서 "Auto FM" 실행
  - 바탕화면 바로가기 동작 확인

- [ ] **기능 검증**
  - 시나리오 입력 및 계산
  - 일반관리비 10% 상한선 적용 확인
  - 이윤 계산 확인
  - 시나리오 저장/로드 (.json 파일)
  - PDF/Excel 내보내기
  - 시나리오 비교 기능

- [ ] **제거 테스트**
  - 제어판 → 프로그램 및 기능 → Auto FM 제거
  - 프로그램 파일 삭제 확인
  - 바로가기 제거 확인
  - 사용자 데이터 보존 확인 (`%LOCALAPPDATA%\auto_fm\`)

---

## 🐛 문제 해결

### PyInstaller 관련

**문제: "PyInstaller: command not found"**
```bash
pip install pyinstaller
```

**문제: "Qt platform plugin could not be initialized"**
- `auto_fm.spec` 파일의 `hiddenimports`에 PyQt6 모듈이 포함되어 있는지 확인
- 현재 spec 파일에는 이미 포함되어 있음

**문제: 파일 크기가 너무 큼 (>200MB)**
- UPX 압축 활성화 확인: `upx=True`
- 불필요한 패키지 제외: `excludes` 목록 추가

### Inno Setup 관련

**문제: "ISCC.exe not found"**
- Inno Setup 6 설치: https://jrsoftware.org/isdl.php
- 설치 경로 확인: `C:\Program Files (x86)\Inno Setup 6\`

**문제: 한글 깨짐**
- `installer.iss` 파일이 UTF-8 인코딩으로 저장되어 있는지 확인
- `[Languages]` 섹션에 `Korean.isl` 설정 확인

### 실행 시 오류

**문제: "database is locked"**
- 이미 해결됨: WAL 모드 활성화됨 (src/domain/db.py)

**문제: 한글 경로 문제**
- pathlib 사용으로 이미 해결됨

---

## 📝 버전 관리

버전 번호 변경 시 다음 파일 수정:

1. **src/version.py**
```python
VERSION = "1.0.0"  # ← 여기 수정
```

2. **installer.iss**
```ini
#define MyAppVersion "1.0.0"  ; ← 여기 수정
```

3. **file_version_info.txt**
```
filevers=(1, 0, 0, 0),  # ← 여기 수정
```

---

## 📦 배포 파일 구조

```
installer_output/
└── AutoFM_Setup_v1.0.0.exe    # 최종 배포 파일

dist/
└── AutoFM.exe                  # 독립 실행 파일 (인스톨러 포함)

build/                          # 빌드 임시 파일 (삭제 가능)
```

---

## 🚀 배포 워크플로우

1. **개발 완료**
   - 모든 테스트 통과 확인
   - 버전 번호 업데이트

2. **빌드**
   ```bash
   build.bat
   ```

3. **로컬 테스트**
   - `dist\AutoFM.exe` 실행 및 기능 확인

4. **인스톨러 생성**
   ```bash
   build_installer.bat
   ```

5. **클린 머신 테스트**
   - Python 미설치 PC에서 인스톨러 실행
   - 전체 기능 검증

6. **배포**
   - `installer_output/AutoFM_Setup_v1.0.0.exe` 배포

---

## 💡 팁

### 빌드 시간 단축
- `--clean` 옵션 제거 (변경 사항이 없을 때)
- UPX 압축 비활성화 (개발 중): `upx=False`

### 디버깅
- 콘솔 모드 활성화: `console=True` (auto_fm.spec)
- 오류 메시지 확인 가능

### 자동화
- CI/CD 파이프라인에 통합 가능
- GitHub Actions 예제:
  ```yaml
  - name: Build executable
    run: |
      pip install pyinstaller
      pyinstaller auto_fm.spec --clean
  ```

---

## 📞 지원

문제 발생 시:
1. 이 문서의 "문제 해결" 섹션 확인
2. 빌드 로그 확인
3. GitHub Issues에 문의

---

**빌드 완료 후 DEPLOY_CHECKLIST.md 문서를 참조하여 배포 전 최종 점검을 수행하세요.**
