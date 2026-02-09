PRAGMA foreign_keys=ON;

-- Minimal deterministic seed for default scenario
INSERT INTO md_job_role (scenario_id, job_code, job_name, sort_order, is_active)
VALUES ('default', 'role', '기본직무', 0, 1);

INSERT INTO md_job_rate (scenario_id, job_code, wage_day, wage_hour, allowance_rate_json)
VALUES ('default', 'role', 0, 0, '{}');

INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'exp_default', '기본경비', 'ETC', 0, 1);

INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'exp_default', 0, 'EA', '2000-01-01', NULL);
