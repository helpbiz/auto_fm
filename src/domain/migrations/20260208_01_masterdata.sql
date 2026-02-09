PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS md_job_role (
  scenario_id TEXT NOT NULL,
  job_code    TEXT NOT NULL,
  job_name    TEXT NOT NULL,
  sort_order  INTEGER NOT NULL DEFAULT 0,
  is_active   INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (scenario_id, job_code)
);

CREATE TABLE IF NOT EXISTS md_job_rate (
  scenario_id TEXT NOT NULL,
  job_code    TEXT NOT NULL,
  wage_day    INTEGER NOT NULL,
  wage_hour   INTEGER NOT NULL,
  allowance_rate_json TEXT NOT NULL,
  PRIMARY KEY (scenario_id, job_code),
  FOREIGN KEY (scenario_id, job_code) REFERENCES md_job_role(scenario_id, job_code) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS md_expense_item (
  scenario_id TEXT NOT NULL,
  exp_code    TEXT NOT NULL,
  exp_name    TEXT NOT NULL,
  group_code  TEXT NOT NULL,
  sort_order  INTEGER NOT NULL DEFAULT 0,
  is_active   INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (scenario_id, exp_code)
);

CREATE TABLE IF NOT EXISTS md_expense_pricebook (
  scenario_id TEXT NOT NULL,
  exp_code    TEXT NOT NULL,
  unit_price  INTEGER NOT NULL,
  unit        TEXT NOT NULL,
  effective_from TEXT NOT NULL,
  effective_to   TEXT,
  PRIMARY KEY (scenario_id, exp_code, effective_from),
  FOREIGN KEY (scenario_id, exp_code) REFERENCES md_expense_item(scenario_id, exp_code) ON DELETE CASCADE
);
