-- 추가 직무코드 등록 (2025년 기준)
-- 부소장, 안전관리자, 품질관리자, 운전기사, 청소원 등

-- year_2025에 추가 직무 등록
INSERT OR IGNORE INTO md_job_role (scenario_id, job_code, job_name, sort_order, is_active)
VALUES
  ('year_2025', 'M102', '부소장', 3, 1),
  ('year_2025', 'T301', '안전관리자', 4, 1),
  ('year_2025', 'T302', '품질관리자', 5, 1),
  ('year_2025', 'D201', '운전기사', 6, 1),
  ('year_2025', 'E502', '청소원', 7, 1);

-- 2025년 노임단가 (wages_master.json 기준)
-- M102(부소장) = 고급기술자 318,000
-- T301(안전관리자) = 중급기술자 269,000
-- T302(품질관리자) = 중급기술자 269,000
-- D201(운전기사) = 단순노무종사원 93,000
-- E502(청소원) = 단순노무종사원 93,000
INSERT OR IGNORE INTO md_job_rate (scenario_id, job_code, wage_day, wage_hour, allowance_rate_json)
VALUES
  ('year_2025', 'M102', 318000, 39750, '{}'),
  ('year_2025', 'T301', 269000, 33625, '{}'),
  ('year_2025', 'T302', 269000, 33625, '{}'),
  ('year_2025', 'D201', 93000, 11625, '{}'),
  ('year_2025', 'E502', 93000, 11625, '{}');

-- year_2024에도 추가 (2024년 노임단가)
INSERT OR IGNORE INTO md_job_role (scenario_id, job_code, job_name, sort_order, is_active)
VALUES
  ('year_2024', 'M102', '부소장', 3, 1),
  ('year_2024', 'T301', '안전관리자', 4, 1),
  ('year_2024', 'T302', '품질관리자', 5, 1),
  ('year_2024', 'D201', '운전기사', 6, 1),
  ('year_2024', 'E502', '청소원', 7, 1);

INSERT OR IGNORE INTO md_job_rate (scenario_id, job_code, wage_day, wage_hour, allowance_rate_json)
VALUES
  ('year_2024', 'M102', 305410, 38176, '{}'),
  ('year_2024', 'T301', 258210, 32276, '{}'),
  ('year_2024', 'T302', 258210, 32276, '{}'),
  ('year_2024', 'D201', 89210, 11151, '{}'),
  ('year_2024', 'E502', 89210, 11151, '{}');

-- year_2023에도 추가
INSERT OR IGNORE INTO md_job_role (scenario_id, job_code, job_name, sort_order, is_active)
VALUES
  ('year_2023', 'M102', '부소장', 3, 1),
  ('year_2023', 'T301', '안전관리자', 4, 1),
  ('year_2023', 'T302', '품질관리자', 5, 1),
  ('year_2023', 'D201', '운전기사', 6, 1),
  ('year_2023', 'E502', '청소원', 7, 1);

INSERT OR IGNORE INTO md_job_rate (scenario_id, job_code, wage_day, wage_hour, allowance_rate_json)
VALUES
  ('year_2023', 'M102', 293753, 36719, '{}'),
  ('year_2023', 'T301', 246709, 30839, '{}'),
  ('year_2023', 'T302', 246709, 30839, '{}'),
  ('year_2023', 'D201', 84618, 10577, '{}'),
  ('year_2023', 'E502', 84618, 10577, '{}');
