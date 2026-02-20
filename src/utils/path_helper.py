# src/utils/path_helper.py
"""
PyInstaller 번들 실행 시 sys._MEIPASS 기반 리소스 경로, 앱 기준 디렉터리 제공.
이미지·엑셀 템플릿 등 번들 리소스는 get_resource_path()로 참조.
"""
import sys
from pathlib import Path
from typing import Union


def _is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def get_app_base_dir() -> Path:
    """
    앱 기준 디렉터리.
    - PyInstaller EXE: 실행 파일(.exe)이 있는 폴더
    - 개발 시: 프로젝트 루트 (auto_fm)
    시나리오·로그·내보내기 등 사용자/쓰기 디렉터리는 이 경로 기준으로 사용.
    """
    if _is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def get_resource_path(*parts: Union[str, Path]) -> Path:
    """
    번들 리소스(이미지, 엑셀 템플릿 등)의 절대 경로.
    - PyInstaller EXE: sys._MEIPASS 내 경로 (spec의 datas로 넣은 파일)
    - 개발 시: 프로젝트 루트 / resources / parts
    spec에 datas=[('resources', 'resources')] 등으로 리소스를 넣으면
    실행 시 MEIPASS/resources/... 로 풀리므로 parts는 ('resources', 'images', 'logo.png') 형태.
    """
    if _is_frozen():
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parents[2] / "resources"
    return base.joinpath(*[str(p) for p in parts])


def get_scenarios_dir() -> Path:
    """시나리오 저장/로드 디렉터리 (app_base/scenarios)."""
    path = get_app_base_dir() / "scenarios"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_exports_dir() -> Path:
    """내보내기 기본 디렉터리 (app_base/exports)."""
    path = get_app_base_dir() / "exports"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_logs_dir() -> Path:
    """로그 디렉터리 (app_base/logs)."""
    path = get_app_base_dir() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_data_dir() -> Path:
    """연도별 단가·직무 매핑 JSON 디렉터리 (app_base/data)."""
    path = get_app_base_dir() / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path
