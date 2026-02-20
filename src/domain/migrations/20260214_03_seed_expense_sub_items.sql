PRAGMA foreign_keys=ON;

-- ===========================================================================
-- 경비 세부 항목 시드 데이터 (Excel auto_fm_fin.xlsx 각 시트 기준)
-- ===========================================================================

DELETE FROM md_expense_sub_item WHERE scenario_id = 'default';

-- ===========================
-- [표20] 피복비 세부
-- ===========================
INSERT INTO md_expense_sub_item (scenario_id, exp_code, sub_code, sub_name, spec, unit, quantity, unit_price, amount, remark, sort_order)
VALUES
('default', 'FIX_WEL_CLOTH', 'CLOTH_SUMMER', '피복비', '하절기', '착', 0.0833, 36500, 3040, '1인×1착/년÷12개월', 1),
('default', 'FIX_WEL_CLOTH', 'CLOTH_SPRING', '피복비', '춘추복', '착', 0.0833, 42500, 3540, '1인×1착/년÷12개월', 2),
('default', 'FIX_WEL_CLOTH', 'CLOTH_WINTER', '피복비', '동절기', '착', 0.0833, 64300, 5356, '1인×1착/년÷12개월', 3),
('default', 'FIX_WEL_CLOTH', 'CLOTH_VEST', '피복비', '조끼', '착', 0.0833, 27500, 2290, '1인×1착/년÷12개월', 4);

-- ===========================
-- [표21] 식대 세부
-- ===========================
INSERT INTO md_expense_sub_item (scenario_id, exp_code, sub_code, sub_name, spec, unit, quantity, unit_price, amount, remark, sort_order)
VALUES
('default', 'FIX_WEL_MEAL', 'MEAL_WEEKDAY', '식대', '평일', '식', 20.6, 6796, 140000, '22식/월', 1),
('default', 'FIX_WEL_MEAL', 'MEAL_HOLIDAY', '식대', '휴일', '식', 1.8, 6796, 12233, '1.8식/월', 2);

-- ===========================
-- [표22] 건강검진비 세부
-- ===========================
INSERT INTO md_expense_sub_item (scenario_id, exp_code, sub_code, sub_name, spec, unit, quantity, unit_price, amount, remark, sort_order)
VALUES
('default', 'FIX_WEL_CHECKUP', 'CHECKUP_01', '건강검진비', '', '회/년', 0.0833, 340000, 28322, '1회/년÷12개월', 1);

-- ===========================
-- [표23] 의약품비 세부
-- ===========================
INSERT INTO md_expense_sub_item (scenario_id, exp_code, sub_code, sub_name, spec, unit, quantity, unit_price, amount, remark, sort_order)
VALUES
('default', 'FIX_WEL_MEDICINE', 'MED_01', '의약품비', '', 'SET/년', 0.0033, 145000, 478, '1SET/년÷12개월÷합계인원', 1);

-- ===========================
-- [표24] 안전관리비 세부
-- ===========================
INSERT INTO md_expense_sub_item (scenario_id, exp_code, sub_code, sub_name, spec, unit, quantity, unit_price, amount, remark, sort_order)
VALUES
('default', 'FIX_SAFETY', 'SAFETY_01', '안전관리비', '직접노무비×지급요율', '식', 1, 1797591, 1797591, '기준금액의 1.86%', 1);

-- ===========================
-- [표25] 교육훈련비 세부
-- ===========================
INSERT INTO md_expense_sub_item (scenario_id, exp_code, sub_code, sub_name, spec, unit, quantity, unit_price, amount, remark, sort_order)
VALUES
('default', 'FIX_TRAINING', 'TRAIN_LEGAL', '법정교육', '건설협회교육', '인/회', 0.0833, 409090, 34077, '1인×1회/년÷12개월', 1),
('default', 'FIX_TRAINING', 'TRAIN_TECH1', '임시교육', '분야별 전문기술 보수교육', '인/회', 0.3333, 100000, 33330, '4인×1회/년÷12개월', 2),
('default', 'FIX_TRAINING', 'TRAIN_MECH', '임시교육', '전문인력양성교육(기계)', '인/회', 0.3333, 100000, 33330, '4인×1회/년÷12개월', 3),
('default', 'FIX_TRAINING', 'TRAIN_ELEC', '임시교육', '전문인력양성교육(전기)', '인/회', 0.3333, 100000, 33330, '4인×1회/년÷12개월', 4),
('default', 'FIX_TRAINING', 'TRAIN_IT', '임시교육', '전문인력양성교육(IT)', '인/회', 0.3333, 100000, 33330, '4인×1회/년÷12개월', 5);

-- ===========================
-- [표26] 소모품비 세부
-- ===========================
INSERT INTO md_expense_sub_item (scenario_id, exp_code, sub_code, sub_name, spec, unit, quantity, unit_price, amount, remark, sort_order)
VALUES
('default', 'FIX_SUPPLIES', 'SUP_PAPER', '복사용지', 'A4박스 외', '식', 1, 206788, 206788, '', 1),
('default', 'FIX_SUPPLIES', 'SUP_OFFICE', '사무용품', '파일 외', '식', 1, 71599, 71599, '', 2),
('default', 'FIX_SUPPLIES', 'SUP_PRINT', '전산처리비', '프린트 토너 외', '식', 1, 334308, 334308, '', 3),
('default', 'FIX_SUPPLIES', 'SUP_ELEC', '전자용품', '키보드/마우스 셑트 외', '식', 1, 8506, 8506, '', 4),
('default', 'FIX_SUPPLIES', 'SUP_ETC', '기타', '제본', '식', 1, 6233, 6233, '', 5);

-- ===========================
-- [표27] 출장여비 세부
-- ===========================
INSERT INTO md_expense_sub_item (scenario_id, exp_code, sub_code, sub_name, spec, unit, quantity, unit_price, amount, remark, sort_order)
VALUES
('default', 'FIX_TRAVEL', 'TRAVEL_SHORT', '근거리출장', '파주시업무(주간보고)', '회/월', 4.3333, 10000, 43333, '1인×52회/년÷12개월', 1),
('default', 'FIX_TRAVEL', 'TRAVEL_MID', '중거리출장', '타시군구 업무', '회/월', 1, 40000, 40000, '1인×12회/년÷12개월', 2),
('default', 'FIX_TRAVEL', 'TRAVEL_LONG', '장거리출장', '선진지 견학(타시도)', '회/월', 0.1666, 74000, 12328, '1인×4회/년÷12개월', 3);

-- ===========================
-- [표29] 통신 및 우편비 세부
-- ===========================
INSERT INTO md_expense_sub_item (scenario_id, exp_code, sub_code, sub_name, spec, unit, quantity, unit_price, amount, remark, sort_order)
VALUES
('default', 'FIX_TELECOM', 'TEL_PHONE', '통신비', '전화 및 팩스', '회선', 2, 60353, 120706, '2회선/월', 1),
('default', 'FIX_TELECOM', 'TEL_INTERNET', '통신비', '인터넷', '회선', 1, 52360, 52360, '1회선/월', 2);

-- ===========================
-- [표30] 소모자재비 세부
-- ===========================
INSERT INTO md_expense_sub_item (scenario_id, exp_code, sub_code, sub_name, spec, unit, quantity, unit_price, amount, remark, sort_order)
VALUES
('default', 'VAR_MATERIAL', 'MAT_TOOL', '소모자재비', '공구 및 계측장비', '식', 1, 4000000, 4000000, '연간', 1),
('default', 'VAR_MATERIAL', 'MAT_ELEC_TOOL', '소모자재비', '전기공구 구입', '식', 1, 4000000, 4000000, '연간', 2),
('default', 'VAR_MATERIAL', 'MAT_REPAIR', '소모자재비', '공구수리', '식', 1, 3000000, 3000000, '연간', 3),
('default', 'VAR_MATERIAL', 'MAT_WORK', '소모자재비', '작업관련 소모자재', '식', 1, 10000000, 10000000, '연간', 4),
('default', 'VAR_MATERIAL', 'MAT_FACILITY', '소모자재비', '기타소모자재(시설물유지)', '식', 1, 6000000, 6000000, '연간', 5);

-- ===========================
-- [표31] 수선유지비 세부 (24년 기준)
-- ===========================
INSERT INTO md_expense_sub_item (scenario_id, exp_code, sub_code, sub_name, spec, unit, quantity, unit_price, amount, remark, sort_order)
VALUES
('default', 'VAR_REPAIR', 'REP_HVAC', '유지관리예비품', '냉난방기류 수리', '식', 1, 10000000, 10000000, '연간', 1),
('default', 'VAR_REPAIR', 'REP_FILTER', '유지관리예비품', '집진필터', '식', 1, 18240000, 18240000, '연간', 2),
('default', 'VAR_REPAIR', 'REP_INLET', '유지관리예비품', '투입구 예비품', '식', 1, 20000000, 20000000, '연간', 3),
('default', 'VAR_REPAIR', 'REP_PIPE', '유지관리예비품', '관크리닝 및 포집백', '식', 1, 15000000, 15000000, '연간', 4),
('default', 'VAR_REPAIR', 'REP_COMPRESSOR', '유지관리예비품', '공기압축기 소모품교체/수리', '식', 1, 50000000, 50000000, '연간', 5),
('default', 'VAR_REPAIR', 'REP_CARBON', '유지관리예비품', '활성탄 교체', '식', 1, 96600000, 96600000, '연간', 6),
('default', 'VAR_REPAIR', 'REP_BLOWER', '유지관리예비품', '송풍기 인버터 수리', '식', 1, 30000000, 30000000, '연간', 7),
('default', 'VAR_REPAIR', 'REP_UPS', '유지관리예비품', '전기실 UPS관련', '식', 1, 10000000, 10000000, '연간', 8),
('default', 'VAR_REPAIR', 'REP_PUMP', '유지관리예비품', '순환펌프 수리', '식', 1, 10000000, 10000000, '연간', 9),
('default', 'VAR_REPAIR', 'REP_FIRE', '유지관리예비품', '소방설비 보수', '식', 1, 5000000, 5000000, '연간', 10),
('default', 'VAR_REPAIR', 'REP_ELEV', '유지관리예비품', '엘리베이터 보수', '식', 1, 3000000, 3000000, '연간', 11),
('default', 'VAR_REPAIR', 'REP_CONTAINER', '유지관리예비품', '컨테이너 이송설비 수리', '식', 1, 40000000, 40000000, '연간', 12),
('default', 'VAR_REPAIR', 'REP_MOTOR', '유지관리예비품', '송풍기 모터 보수', '식', 1, 30000000, 30000000, '연간', 13),
('default', 'VAR_REPAIR', 'REP_COMM', '유지관리예비품', '통신관련 수리,구매', '식', 1, 20000000, 20000000, '연간', 14),
('default', 'VAR_REPAIR', 'REP_FACILITY', '유지관리예비품', '운영관련 시설물 유지비', '식', 1, 8000000, 8000000, '연간', 15),
('default', 'VAR_REPAIR', 'REP_LOCAL_EXHAUST', '유지관리예비품', '국소배기 보수', '식', 1, 20000000, 20000000, '연간', 16),
('default', 'VAR_REPAIR', 'REP_DEODORIZE', '유지관리예비품', '세정식탈취설비 수리', '식', 1, 20000000, 20000000, '연간', 17),
('default', 'VAR_REPAIR', 'REP_COMPACTOR', '유지관리예비품', '컴팩터 관련 수리', '식', 1, 20000000, 20000000, '연간', 18),
('default', 'VAR_REPAIR', 'REP_AUTO_CTRL', '유지관리예비품', '자동제어 관련 수리 보수', '식', 1, 50000000, 50000000, '연간', 19),
('default', 'VAR_REPAIR', 'REP_CENTRIFUGE', '유지관리예비품', '원심분리수 보수', '식', 1, 60000000, 60000000, '연간', 20),
('default', 'VAR_REPAIR', 'REP_VALVE', '유지관리예비품', '전환밸브 보수', '식', 1, 80000000, 80000000, '연간', 21),
('default', 'VAR_REPAIR', 'REP_BUILDING', '유지관리예비품', '건축물 설비 보수', '식', 1, 20000000, 20000000, '연간', 22);

-- ===========================
-- [표32] 측정검사수수료 세부
-- ===========================
INSERT INTO md_expense_sub_item (scenario_id, exp_code, sub_code, sub_name, spec, unit, quantity, unit_price, amount, remark, sort_order)
VALUES
('default', 'VAR_INSPECT', 'INS_ELEVATOR', '측정검사수수료', '승강기 정기안전검사', '회', 1, 109600, 109600, '1회/년×1개소', 1),
('default', 'VAR_INSPECT', 'INS_ELEC_SAFETY', '측정검사수수료', '전기안전정기검사', '회', 1.3333, 994200, 1325566, '1회×4개소÷3년', 2),
('default', 'VAR_INSPECT', 'INS_COMP_TANK', '측정검사수수료', '공기압축기탱크 정기검사', '회', 2, 66000, 132000, '1회/2년×4개소', 3),
('default', 'VAR_INSPECT', 'INS_HOIST', '측정검사수수료', '호이스트 정기검사', '회', 2, 118000, 236000, '1회/2년×4개소', 4);

-- ===========================
-- [표33] 안전점검대행비 세부
-- ===========================
INSERT INTO md_expense_sub_item (scenario_id, exp_code, sub_code, sub_name, spec, unit, quantity, unit_price, amount, remark, sort_order)
VALUES
('default', 'VAR_SAFETY_AGENT', 'SA_ELEC1', '전기안전점검대행', '제1집하장', '회', 12, 530000, 6360000, '1회×12개월', 1),
('default', 'VAR_SAFETY_AGENT', 'SA_ELEC2', '전기안전점검대행', '제2집하장', '회', 12, 530000, 6360000, '1회×12개월', 2),
('default', 'VAR_SAFETY_AGENT', 'SA_ELEC3', '전기안전점검대행', '제3집하장', '회', 12, 530000, 6360000, '1회×12개월', 3),
('default', 'VAR_SAFETY_AGENT', 'SA_ELEC4', '전기안전점검대행', '제4집하장', '회', 12, 530000, 6360000, '1회×12개월', 4),
('default', 'VAR_SAFETY_AGENT', 'SA_ELEV', '승강기유지보수', '제1집하장', '회', 12, 170000, 2040000, '1회×12개월', 5),
('default', 'VAR_SAFETY_AGENT', 'SA_FIRE', '소방안전관리대행', '제1-4집하장', '회', 48, 37500, 1800000, '12회/년×4개소', 6);

-- ===========================
-- [표34] 차량유지비 세부
-- ===========================
INSERT INTO md_expense_sub_item (scenario_id, exp_code, sub_code, sub_name, spec, unit, quantity, unit_price, amount, remark, sort_order)
VALUES
('default', 'VAR_VEHICLE', 'VEH_LEASE1', '차량리스비', '봉고3 초장축 더블캡(1톤)', '대/월', 48, 479000, 22992000, '4대×12개월', 1),
('default', 'VAR_VEHICLE', 'VEH_LEASE2', '차량리스비', '봉고3 초장축 싱글캡(1톤)', '대/월', 12, 473000, 5676000, '1대×12개월', 2),
('default', 'VAR_VEHICLE', 'VEH_LEASE3', '차량리스비', '스포티지 가솔린(1.6터보)', '대/월', 12, 808000, 9696000, '1대×12개월', 3),
('default', 'VAR_VEHICLE', 'VEH_FUEL_DIESEL', '유류비', '업무용 트럭(경유)', 'ℓ', 12000, 1400, 16800000, '5대×약200ℓ/월×12개월', 4),
('default', 'VAR_VEHICLE', 'VEH_FUEL_GAS', '유류비', '업무용 차량(가솔린)', 'ℓ', 2400, 1585, 3804000, '1대×약200ℓ/월×12개월', 5),
('default', 'VAR_VEHICLE', 'VEH_REPAIR', '차량수리비', '사고 자차 및 소손 수리', '식', 6, 50000, 300000, '', 6);

-- ===========================
-- [표35] 보안관리비 세부
-- ===========================
INSERT INTO md_expense_sub_item (scenario_id, exp_code, sub_code, sub_name, spec, unit, quantity, unit_price, amount, remark, sort_order)
VALUES
('default', 'VAR_SECURITY', 'SEC_ADT', '보안관리비', 'ADT 캡스', '회', 48, 130000, 6240000, '4집하장×12개월', 1);

-- ===========================
-- [표36] 수집운반비 세부
-- ===========================
INSERT INTO md_expense_sub_item (scenario_id, exp_code, sub_code, sub_name, spec, unit, quantity, unit_price, amount, remark, sort_order)
VALUES
('default', 'VAR_TRANSPORT', 'TRANS_TAX', '세금과공과', '', '회', 1, 8398637, 8398637, '연간', 1),
('default', 'VAR_TRANSPORT', 'TRANS_DEPREC', '감가상각비', '', '회', 1, 7944145, 7944145, '3대×12개월', 2),
('default', 'VAR_TRANSPORT', 'TRANS_FUEL', '유류비', '', '회', 34200, 1400, 47880000, '3대×약950ℓ/월×12개월', 3),
('default', 'VAR_TRANSPORT', 'TRANS_REPAIR', '수리수선비', '', '회', 1, 110000, 110000, '연간', 4),
('default', 'VAR_TRANSPORT', 'TRANS_ETC', '기타경비', '', '식', 1, 5371750, 5371750, '집계표참조', 5);

-- ===========================
-- [표37] 전력비 세부
-- ===========================
INSERT INTO md_expense_sub_item (scenario_id, exp_code, sub_code, sub_name, spec, unit, quantity, unit_price, amount, remark, sort_order)
VALUES
('default', 'PASS_ELECTRIC', 'ELEC_BASE', '기본요금', '', 'kw/년', 32626, 8320, 271444292, '8,156.5kw/년×4개소', 1),
('default', 'PASS_ELECTRIC', 'ELEC_RESERVE', '예비요금', '', '식', 1, 17157596, 17157596, '', 2),
('default', 'PASS_ELECTRIC', 'ELEC_USE1', '사용요금', '제1집하장', 'kw/년', 2205343, 121, 267368373, '', 3),
('default', 'PASS_ELECTRIC', 'ELEC_USE2', '사용요금', '제2집하장', 'kw/년', 3728815, 121, 452069040, '', 4),
('default', 'PASS_ELECTRIC', 'ELEC_USE3', '사용요금', '제3집하장', 'kw/년', 2123699, 121, 257470127, '', 5),
('default', 'PASS_ELECTRIC', 'ELEC_USE4', '사용요금', '제4집하장', 'kw/년', 2915602, 121, 353477807, '', 6);

-- ===========================
-- [표39] 수도광열비 세부
-- ===========================
INSERT INTO md_expense_sub_item (scenario_id, exp_code, sub_code, sub_name, spec, unit, quantity, unit_price, amount, remark, sort_order)
VALUES
('default', 'PASS_WATER', 'WATER_BASE1', '상수도사용료', '정액요금(제1집하장D40)', '개소', 12, 16300, 195600, '1개소×12개월', 1),
('default', 'PASS_WATER', 'WATER_BASE2', '상수도사용료', '정액요금(제2-4집하장D32)', '개소', 36, 10250, 369000, '3개소×12개월', 2),
('default', 'PASS_WATER', 'WATER_USE', '상수도사용료', '사용요금', '㎥/월', 21600, 646, 13953600, '450㎥/h×4개소×12개월', 3),
('default', 'PASS_WATER', 'WATER_FEE', '상수도사용료', '물이용부담금', '㎥/월', 21600, 49, 1058400, '450㎥/h×4개소×12개월', 4),
('default', 'PASS_WATER', 'SEWER_USE', '하수도사용료', '사용요금', '㎥/월', 21600, 895, 19332000, '450㎥/월×4개소×12개월', 5),
('default', 'PASS_WATER', 'GAS_HEAT', '도시가스', '냉난방용(제1집하장)', '㎥', 5400, 1628, 8792010, '450㎥(월평균)×12개월', 6);

-- ===========================
-- [표40] 시설물보험료 세부
-- ===========================
INSERT INTO md_expense_sub_item (scenario_id, exp_code, sub_code, sub_name, spec, unit, quantity, unit_price, amount, remark, sort_order)
VALUES
('default', 'PASS_FACILITY_INS', 'FINS_FIRE1', '공장화재보험', '제1집하장:2,410.00㎡', '식', 1, 9414829, 9414829, '', 1),
('default', 'PASS_FACILITY_INS', 'FINS_FIRE2', '공장화재보험', '제2집하장:1,458.56㎡', '식', 1, 5424860, 5424860, '', 2),
('default', 'PASS_FACILITY_INS', 'FINS_FIRE3', '공장화재보험', '제3집하장:1,435.39㎡', '식', 1, 5214874, 5214874, '', 3),
('default', 'PASS_FACILITY_INS', 'FINS_FIRE4', '공장화재보험', '제4집하장:1,449.49㎡', '식', 1, 4995104, 4995104, '', 4),
('default', 'PASS_FACILITY_INS', 'FINS_PROP1', '동산종합보험', '제1집하장', '식', 1, 9664057, 9664057, '', 5),
('default', 'PASS_FACILITY_INS', 'FINS_PROP2', '동산종합보험', '제2집하장', '식', 1, 11791300, 11791300, '', 6),
('default', 'PASS_FACILITY_INS', 'FINS_PROP3', '동산종합보험', '제3집하장', '식', 1, 8499015, 8499015, '', 7),
('default', 'PASS_FACILITY_INS', 'FINS_PROP4', '동산종합보험', '제4집하장', '식', 1, 7436228, 7436228, '', 8),
('default', 'PASS_FACILITY_INS', 'FINS_LIABILITY', '화재배상보험', '공통', '식', 1, 107233, 107233, '', 9),
('default', 'PASS_FACILITY_INS', 'FINS_BIZ_LIABILITY', '영업배상보험', '공통(주관로52.49km,시설면적6,741㎡)', '식', 1, 7440000, 7440000, '', 10);
