CREATE TABLE IF NOT EXISTS calculation_result (
  scenario_id TEXT PRIMARY KEY,
  result_json TEXT NOT NULL,
  updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
