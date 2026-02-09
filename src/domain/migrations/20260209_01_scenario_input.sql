CREATE TABLE IF NOT EXISTS scenario_input (
  scenario_id TEXT PRIMARY KEY,
  input_json  TEXT NOT NULL,
  updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
