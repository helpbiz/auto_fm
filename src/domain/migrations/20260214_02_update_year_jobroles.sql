-- year_2023 / year_2024 / year_2025 시나리오에 17개 직무코드 적용
-- 엑셀 '투입인원' 시트 기반 직무코드(MGR/OPS/ENV/TRN) 체계
-- wages_master.json 기술등급별 노임단가 반영
PRAGMA foreign_keys=ON;

-- ============================================================
-- year_2023
-- ============================================================
DELETE FROM md_job_rate WHERE scenario_id = 'year_2023';
DELETE FROM md_job_role WHERE scenario_id = 'year_2023';
DELETE FROM scenario_input WHERE scenario_id = 'year_2023';
DELETE FROM calculation_result WHERE scenario_id = 'year_2023';

INSERT INTO md_job_role (scenario_id, job_code, job_name, sort_order, is_active) VALUES
  ('year_2023', 'MGR01', '관리소장', 1, 1),
  ('year_2023', 'MGR02', '관리팀장', 2, 1),
  ('year_2023', 'MGR03', '관리팀원', 3, 1),
  ('year_2023', 'OPS01', '전기팀장', 4, 1),
  ('year_2023', 'OPS02', '기계팀장', 5, 1),
  ('year_2023', 'OPS03', '전기담당', 6, 1),
  ('year_2023', 'OPS04', '기계담당', 7, 1),
  ('year_2023', 'OPS05', '전기담당', 8, 1),
  ('year_2023', 'OPS06', '기계담당', 9, 1),
  ('year_2023', 'OPS07', '전기담당', 10, 1),
  ('year_2023', 'OPS08', '기계담당', 11, 1),
  ('year_2023', 'OPS09', '전기담당', 12, 1),
  ('year_2023', 'OPS10', '기계담당', 13, 1),
  ('year_2023', 'ENV01', '환경팀장', 14, 1),
  ('year_2023', 'ENV02', '환경팀원', 15, 1),
  ('year_2023', 'TRN01', '운전원', 16, 1),
  ('year_2023', 'TRN02', '운반팀원', 17, 1);

INSERT INTO md_job_rate (scenario_id, job_code, wage_day, wage_hour, allowance_rate_json) VALUES
  ('year_2023', 'MGR01', 293753, 36719, '{}'),
  ('year_2023', 'MGR02', 293753, 36719, '{}'),
  ('year_2023', 'MGR03', 183671, 22958, '{}'),
  ('year_2023', 'OPS01', 246709, 30838, '{}'),
  ('year_2023', 'OPS02', 246709, 30838, '{}'),
  ('year_2023', 'OPS03', 217342, 27167, '{}'),
  ('year_2023', 'OPS04', 217342, 27167, '{}'),
  ('year_2023', 'OPS05', 234982, 29372, '{}'),
  ('year_2023', 'OPS06', 234982, 29372, '{}'),
  ('year_2023', 'OPS07', 209077, 26134, '{}'),
  ('year_2023', 'OPS08', 209077, 26134, '{}'),
  ('year_2023', 'OPS09', 183671, 22958, '{}'),
  ('year_2023', 'OPS10', 183671, 22958, '{}'),
  ('year_2023', 'ENV01', 183671, 22958, '{}'),
  ('year_2023', 'ENV02', 84618, 10577, '{}'),
  ('year_2023', 'TRN01', 183671, 22958, '{}'),
  ('year_2023', 'TRN02', 84618, 10577, '{}');

-- ============================================================
-- year_2024
-- ============================================================
DELETE FROM md_job_rate WHERE scenario_id = 'year_2024';
DELETE FROM md_job_role WHERE scenario_id = 'year_2024';
DELETE FROM scenario_input WHERE scenario_id = 'year_2024';
DELETE FROM calculation_result WHERE scenario_id = 'year_2024';

INSERT INTO md_job_role (scenario_id, job_code, job_name, sort_order, is_active) VALUES
  ('year_2024', 'MGR01', '관리소장', 1, 1),
  ('year_2024', 'MGR02', '관리팀장', 2, 1),
  ('year_2024', 'MGR03', '관리팀원', 3, 1),
  ('year_2024', 'OPS01', '전기팀장', 4, 1),
  ('year_2024', 'OPS02', '기계팀장', 5, 1),
  ('year_2024', 'OPS03', '전기담당', 6, 1),
  ('year_2024', 'OPS04', '기계담당', 7, 1),
  ('year_2024', 'OPS05', '전기담당', 8, 1),
  ('year_2024', 'OPS06', '기계담당', 9, 1),
  ('year_2024', 'OPS07', '전기담당', 10, 1),
  ('year_2024', 'OPS08', '기계담당', 11, 1),
  ('year_2024', 'OPS09', '전기담당', 12, 1),
  ('year_2024', 'OPS10', '기계담당', 13, 1),
  ('year_2024', 'ENV01', '환경팀장', 14, 1),
  ('year_2024', 'ENV02', '환경팀원', 15, 1),
  ('year_2024', 'TRN01', '운전원', 16, 1),
  ('year_2024', 'TRN02', '운반팀원', 17, 1);

INSERT INTO md_job_rate (scenario_id, job_code, wage_day, wage_hour, allowance_rate_json) VALUES
  ('year_2024', 'MGR01', 305410, 38176, '{}'),
  ('year_2024', 'MGR02', 305410, 38176, '{}'),
  ('year_2024', 'MGR03', 192210, 24026, '{}'),
  ('year_2024', 'OPS01', 258210, 32276, '{}'),
  ('year_2024', 'OPS02', 258210, 32276, '{}'),
  ('year_2024', 'OPS03', 225110, 28138, '{}'),
  ('year_2024', 'OPS04', 225110, 28138, '{}'),
  ('year_2024', 'OPS05', 246010, 30751, '{}'),
  ('year_2024', 'OPS06', 246010, 30751, '{}'),
  ('year_2024', 'OPS07', 219560, 27445, '{}'),
  ('year_2024', 'OPS08', 219560, 27445, '{}'),
  ('year_2024', 'OPS09', 192210, 24026, '{}'),
  ('year_2024', 'OPS10', 192210, 24026, '{}'),
  ('year_2024', 'ENV01', 192210, 24026, '{}'),
  ('year_2024', 'ENV02', 89210, 11151, '{}'),
  ('year_2024', 'TRN01', 192210, 24026, '{}'),
  ('year_2024', 'TRN02', 89210, 11151, '{}');

-- ============================================================
-- year_2025
-- ============================================================
DELETE FROM md_job_rate WHERE scenario_id = 'year_2025';
DELETE FROM md_job_role WHERE scenario_id = 'year_2025';
DELETE FROM scenario_input WHERE scenario_id = 'year_2025';
DELETE FROM calculation_result WHERE scenario_id = 'year_2025';

INSERT INTO md_job_role (scenario_id, job_code, job_name, sort_order, is_active) VALUES
  ('year_2025', 'MGR01', '관리소장', 1, 1),
  ('year_2025', 'MGR02', '관리팀장', 2, 1),
  ('year_2025', 'MGR03', '관리팀원', 3, 1),
  ('year_2025', 'OPS01', '전기팀장', 4, 1),
  ('year_2025', 'OPS02', '기계팀장', 5, 1),
  ('year_2025', 'OPS03', '전기담당', 6, 1),
  ('year_2025', 'OPS04', '기계담당', 7, 1),
  ('year_2025', 'OPS05', '전기담당', 8, 1),
  ('year_2025', 'OPS06', '기계담당', 9, 1),
  ('year_2025', 'OPS07', '전기담당', 10, 1),
  ('year_2025', 'OPS08', '기계담당', 11, 1),
  ('year_2025', 'OPS09', '전기담당', 12, 1),
  ('year_2025', 'OPS10', '기계담당', 13, 1),
  ('year_2025', 'ENV01', '환경팀장', 14, 1),
  ('year_2025', 'ENV02', '환경팀원', 15, 1),
  ('year_2025', 'TRN01', '운전원', 16, 1),
  ('year_2025', 'TRN02', '운반팀원', 17, 1);

INSERT INTO md_job_rate (scenario_id, job_code, wage_day, wage_hour, allowance_rate_json) VALUES
  ('year_2025', 'MGR01', 318000, 39750, '{}'),
  ('year_2025', 'MGR02', 318000, 39750, '{}'),
  ('year_2025', 'MGR03', 201000, 25125, '{}'),
  ('year_2025', 'OPS01', 269000, 33625, '{}'),
  ('year_2025', 'OPS02', 269000, 33625, '{}'),
  ('year_2025', 'OPS03', 234000, 29250, '{}'),
  ('year_2025', 'OPS04', 234000, 29250, '{}'),
  ('year_2025', 'OPS05', 254000, 31750, '{}'),
  ('year_2025', 'OPS06', 254000, 31750, '{}'),
  ('year_2025', 'OPS07', 229000, 28625, '{}'),
  ('year_2025', 'OPS08', 229000, 28625, '{}'),
  ('year_2025', 'OPS09', 201000, 25125, '{}'),
  ('year_2025', 'OPS10', 201000, 25125, '{}'),
  ('year_2025', 'ENV01', 201000, 25125, '{}'),
  ('year_2025', 'ENV02', 93000, 11625, '{}'),
  ('year_2025', 'TRN01', 201000, 25125, '{}'),
  ('year_2025', 'TRN02', 93000, 11625, '{}');
