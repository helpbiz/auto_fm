-- M101(소장/고급기술자), E501(환경원/단순노무종사원) 기본 등록
-- JOB_META 표시용; 일급은 2024년 기준 단가 반영
INSERT OR IGNORE INTO md_job_role (scenario_id, job_code, job_name, sort_order, is_active)
VALUES
  ('default', 'M101', '소장', 1, 1),
  ('default', 'E501', '환경원', 2, 1);

INSERT OR IGNORE INTO md_job_rate (scenario_id, job_code, wage_day, wage_hour, allowance_rate_json)
VALUES
  ('default', 'M101', 293753, 0, '{}'),
  ('default', 'E501', 84618, 0, '{}');
