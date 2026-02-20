-- 투입인원 시트 기반 직무코드 매핑 업데이트
-- 엑셀 '투입인원' 시트의 17개 직책을 md_job_role / md_job_rate에 반영
-- default 시나리오만 대상
PRAGMA foreign_keys=ON;

-- 1. 기존 default 시나리오 직무 데이터 삭제 (FK 제약: rate 먼저)
DELETE FROM md_job_rate WHERE scenario_id = 'default';
DELETE FROM md_job_role WHERE scenario_id = 'default';

-- 2. 기존 default 시나리오 산출 캐시 초기화 (직무코드 변경으로 무효)
DELETE FROM scenario_input WHERE scenario_id = 'default';
DELETE FROM calculation_result WHERE scenario_id = 'default';

-- 3. 17개 직무 INSERT (md_job_role)
-- job_code 체계: MGR=관리팀, OPS=운영팀, ENV=환경팀, TRN=운반팀
INSERT INTO md_job_role (scenario_id, job_code, job_name, sort_order, is_active) VALUES
  ('default', 'MGR01', '관리소장', 1, 1),
  ('default', 'MGR02', '관리팀장', 2, 1),
  ('default', 'MGR03', '관리팀원', 3, 1),
  ('default', 'OPS01', '전기팀장', 4, 1),
  ('default', 'OPS02', '기계팀장', 5, 1),
  ('default', 'OPS03', '전기담당', 6, 1),
  ('default', 'OPS04', '기계담당', 7, 1),
  ('default', 'OPS05', '전기담당', 8, 1),
  ('default', 'OPS06', '기계담당', 9, 1),
  ('default', 'OPS07', '전기담당', 10, 1),
  ('default', 'OPS08', '기계담당', 11, 1),
  ('default', 'OPS09', '전기담당', 12, 1),
  ('default', 'OPS10', '기계담당', 13, 1),
  ('default', 'ENV01', '환경팀장', 14, 1),
  ('default', 'ENV02', '환경팀원', 15, 1),
  ('default', 'TRN01', '운전원', 16, 1),
  ('default', 'TRN02', '운반팀원', 17, 1);

-- 4. 17개 임률 INSERT (md_job_rate)
-- wage_day: 엔지니어링기술자 환경부문 노임단가 2023
-- wage_hour: wage_day / 8 (1원 미만 절사)
INSERT INTO md_job_rate (scenario_id, job_code, wage_day, wage_hour, allowance_rate_json) VALUES
  ('default', 'MGR01', 293753, 36719, '{}'),
  ('default', 'MGR02', 293753, 36719, '{}'),
  ('default', 'MGR03', 183671, 22958, '{}'),
  ('default', 'OPS01', 246709, 30838, '{}'),
  ('default', 'OPS02', 246709, 30838, '{}'),
  ('default', 'OPS03', 217342, 27167, '{}'),
  ('default', 'OPS04', 217342, 27167, '{}'),
  ('default', 'OPS05', 234982, 29372, '{}'),
  ('default', 'OPS06', 234982, 29372, '{}'),
  ('default', 'OPS07', 209077, 26134, '{}'),
  ('default', 'OPS08', 209077, 26134, '{}'),
  ('default', 'OPS09', 183671, 22958, '{}'),
  ('default', 'OPS10', 183671, 22958, '{}'),
  ('default', 'ENV01', 183671, 22958, '{}'),
  ('default', 'ENV02', 84618, 10577, '{}'),
  ('default', 'TRN01', 183671, 22958, '{}'),
  ('default', 'TRN02', 84618, 10577, '{}');
