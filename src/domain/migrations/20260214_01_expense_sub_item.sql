-- 경비 항목별 세부 내역 테이블
-- 각 경비 항목(md_expense_item)의 세부 구성 항목을 저장
-- 예: 피복비 → 하절기/춘추복/동절기/조끼, 수선유지비 → 냉난방기류수리/집진필터/...

CREATE TABLE IF NOT EXISTS md_expense_sub_item (
  scenario_id  TEXT    NOT NULL,
  exp_code     TEXT    NOT NULL,
  sub_code     TEXT    NOT NULL,
  sub_name     TEXT    NOT NULL,
  spec         TEXT    NOT NULL DEFAULT '',
  unit         TEXT    NOT NULL DEFAULT '식',
  quantity     REAL    NOT NULL DEFAULT 0,
  unit_price   INTEGER NOT NULL DEFAULT 0,
  amount       INTEGER NOT NULL DEFAULT 0,
  remark       TEXT    NOT NULL DEFAULT '',
  sort_order   INTEGER NOT NULL DEFAULT 0,
  is_active    INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (scenario_id, exp_code, sub_code),
  FOREIGN KEY (scenario_id, exp_code) REFERENCES md_expense_item(scenario_id, exp_code) ON DELETE CASCADE
);
