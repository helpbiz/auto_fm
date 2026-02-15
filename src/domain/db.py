import logging
import os
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


APP_NAME = "auto_fm"

# 로그 중복 방지: 이미 로그한 경로/디렉터리
_logged_db_paths: set = set()
_logged_db_dirs: set = set()


def get_app_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def _get_legacy_db_path() -> Path:
    base_dir = get_app_base_dir()
    return base_dir / "data" / "app.db"


def _get_default_db_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / APP_NAME
    return get_app_base_dir() / "data"


def _ensure_writable_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    test_file = path / "._write_test"
    try:
        test_file.write_text("ok", encoding="utf-8")
        key = str(path.resolve())
        if key not in _logged_db_dirs:
            logging.debug("DB dir writable: %s", path)
            _logged_db_dirs.add(key)
    finally:
        if test_file.exists():
            test_file.unlink()


def _migrate_legacy_db(new_path: Path) -> None:
    legacy_path = _get_legacy_db_path()
    if legacy_path.exists() and not new_path.exists():
        new_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(legacy_path, new_path)
        logging.info("DB migrated: %s -> %s", legacy_path, new_path)


def get_db_path() -> Path:
    override = os.environ.get("COSTCALC_DB_PATH")
    if override:
        path = Path(override)
        _ensure_writable_dir(path.parent)
        key = str(path.resolve())
        if key not in _logged_db_paths:
            logging.debug("DB path resolved: %s", path)
            _logged_db_paths.add(key)
        return path

    data_dir = _get_default_db_dir()
    _ensure_writable_dir(data_dir)
    db_path = data_dir / "app.db"
    _migrate_legacy_db(db_path)
    key = str(db_path.resolve())
    if key not in _logged_db_paths:
        logging.debug("DB path resolved: %s", db_path)
        _logged_db_paths.add(key)
    return db_path


def get_connection() -> sqlite3.Connection:
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, timeout=30)
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
    except sqlite3.OperationalError:
        conn.execute("PRAGMA journal_mode=DELETE;")
    return conn


def get_conn() -> sqlite3.Connection:
    return get_connection()


def startup_verification(debug: bool) -> None:
    if not debug:
        return
    db_path = get_db_path()
    try:
        conn = get_connection()
        try:
            journal_mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
            integrity = conn.execute("PRAGMA integrity_check;").fetchone()[0]
            conn.execute(
                "CREATE TABLE IF NOT EXISTS _health_check (k TEXT PRIMARY KEY, v TEXT)"
            )
            conn.execute(
                "INSERT OR REPLACE INTO _health_check (k, v) VALUES (?, ?)",
                ("startup", datetime.utcnow().isoformat()),
            )
            conn.commit()
            logging.info(
                "DB startup check: path=%s journal_mode=%s integrity=%s",
                db_path,
                journal_mode,
                integrity,
            )
        finally:
            conn.close()
    except sqlite3.OperationalError as exc:
        logging.error("DB startup check failed: %s (%s)", db_path, exc)


def _integrity_check(db_path: Path) -> str:
    conn = sqlite3.connect(db_path, timeout=5)
    try:
        return conn.execute("PRAGMA integrity_check;").fetchone()[0]
    finally:
        conn.close()


def handle_disk_io_error(db_path: Path) -> None:
    _ensure_writable_dir(db_path.parent)
    try:
        integrity = _integrity_check(db_path)
    except sqlite3.OperationalError as exc:
        logging.error("DB integrity check failed: %s (%s)", db_path, exc)
        integrity = "error"

    if integrity != "ok":
        stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        backup_path = db_path.with_suffix(f".corrupt-{stamp}.db")
        if db_path.exists():
            shutil.copy2(db_path, backup_path)
            db_path.unlink(missing_ok=True)
            logging.error("DB corrupted, backed up to: %s", backup_path)

        conn = get_connection()
        conn.close()
