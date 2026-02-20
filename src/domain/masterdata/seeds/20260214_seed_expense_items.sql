PRAGMA foreign_keys=ON;

-- ===========================================================================
-- 경비 항목 시드 데이터 (Excel auto_fm_fin.xlsx 경비집계표 기준)
-- 기존 default 경비 항목 삭제 후 실제 항목으로 교체
-- ===========================================================================

DELETE FROM md_expense_pricebook WHERE scenario_id = 'default';
DELETE FROM md_expense_item WHERE scenario_id = 'default';

-- ===========================
-- 고정경비 (FIXED)
-- ===========================

-- [표17] 인적보험료 - 산재보험료
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'FIX_INS_INDUST', '산재보험료', 'FIXED', 100, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'FIX_INS_INDUST', 0, '원/인·월', '2024-01-01', NULL);

-- [표17] 인적보험료 - 국민연금
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'FIX_INS_PENSION', '국민연금', 'FIXED', 101, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'FIX_INS_PENSION', 0, '원/인·월', '2024-01-01', NULL);

-- [표17] 인적보험료 - 고용보험료
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'FIX_INS_EMPLOY', '고용보험료', 'FIXED', 102, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'FIX_INS_EMPLOY', 0, '원/인·월', '2024-01-01', NULL);

-- [표17] 인적보험료 - 국민건강보험료
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'FIX_INS_HEALTH', '국민건강보험료', 'FIXED', 103, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'FIX_INS_HEALTH', 0, '원/인·월', '2024-01-01', NULL);

-- [표17] 인적보험료 - 노인장기요양보험료
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'FIX_INS_LONGTERM', '노인장기요양보험료', 'FIXED', 104, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'FIX_INS_LONGTERM', 0, '원/인·월', '2024-01-01', NULL);

-- [표17] 인적보험료 - 임금채권보장보험료
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'FIX_INS_WAGE', '임금채권보장보험료', 'FIXED', 105, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'FIX_INS_WAGE', 0, '원/인·월', '2024-01-01', NULL);

-- [표17] 인적보험료 - 석면피해구제분담금
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'FIX_INS_ASBESTOS', '석면피해구제분담금', 'FIXED', 106, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'FIX_INS_ASBESTOS', 0, '원/인·월', '2024-01-01', NULL);

-- [표19~23] 복리후생비 - 피복비
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'FIX_WEL_CLOTH', '피복비', 'FIXED', 200, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'FIX_WEL_CLOTH', 14226, '원/인·월', '2024-01-01', NULL);

-- [표19~23] 복리후생비 - 식대
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'FIX_WEL_MEAL', '식대', 'FIXED', 201, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'FIX_WEL_MEAL', 152233, '원/인·월', '2024-01-01', NULL);

-- [표19~23] 복리후생비 - 건강검진비
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'FIX_WEL_CHECKUP', '건강검진비', 'FIXED', 202, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'FIX_WEL_CHECKUP', 28322, '원/인·월', '2024-01-01', NULL);

-- [표19~23] 복리후생비 - 의약품비
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'FIX_WEL_MEDICINE', '의약품비', 'FIXED', 203, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'FIX_WEL_MEDICINE', 478, '원/인·월', '2024-01-01', NULL);

-- [표24] 안전관리비
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'FIX_SAFETY', '안전관리비', 'FIXED', 300, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'FIX_SAFETY', 1797591, '원/월', '2024-01-01', NULL);

-- [표25] 교육훈련비
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'FIX_TRAINING', '교육훈련비', 'FIXED', 400, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'FIX_TRAINING', 167397, '원/월', '2024-01-01', NULL);

-- [표26] 소모품비
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'FIX_SUPPLIES', '소모품비', 'FIXED', 500, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'FIX_SUPPLIES', 627434, '원/월', '2024-01-01', NULL);

-- [표27] 출장여비
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'FIX_TRAVEL', '출장여비', 'FIXED', 600, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'FIX_TRAVEL', 95661, '원/월', '2024-01-01', NULL);

-- [표29] 통신 및 우편비
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'FIX_TELECOM', '통신 및 우편비', 'FIXED', 700, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'FIX_TELECOM', 173066, '원/월', '2024-01-01', NULL);


-- ===========================
-- 변동경비 (VARIABLE)
-- ===========================

-- [표30] 소모자재비
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'VAR_MATERIAL', '소모자재비', 'VARIABLE', 1000, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'VAR_MATERIAL', 2250000, '원/월', '2024-01-01', NULL);

-- [표31] 수선유지비
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'VAR_REPAIR', '수선유지비', 'VARIABLE', 1100, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'VAR_REPAIR', 52986666, '원/월', '2024-01-01', NULL);

-- [표32] 측정검사수수료
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'VAR_INSPECT', '측정검사수수료', 'VARIABLE', 1200, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'VAR_INSPECT', 150263, '원/월', '2024-01-01', NULL);

-- [표33] 안전점검대행비
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'VAR_SAFETY_AGENT', '안전점검대행비', 'VARIABLE', 1300, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'VAR_SAFETY_AGENT', 2440000, '원/월', '2024-01-01', NULL);

-- [표34] 차량유지비
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'VAR_VEHICLE', '차량유지비', 'VARIABLE', 1400, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'VAR_VEHICLE', 4939000, '원/월', '2024-01-01', NULL);

-- [표35] 보안관리비
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'VAR_SECURITY', '보안관리비', 'VARIABLE', 1500, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'VAR_SECURITY', 520000, '원/월', '2024-01-01', NULL);

-- [표36] 수집운반비
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'VAR_TRANSPORT', '수집운반비', 'VARIABLE', 1600, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'VAR_TRANSPORT', 5808711, '원/월', '2024-01-01', NULL);


-- ===========================
-- 대납분 (PASSTHROUGH)
-- ===========================

-- [표37] 전력비
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'PASS_ELECTRIC', '전력비', 'PASSTHROUGH', 2000, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'PASS_ELECTRIC', 134915602, '원/월', '2024-01-01', NULL);

-- [표39] 수도광열비
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'PASS_WATER', '수도광열비', 'PASSTHROUGH', 2100, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'PASS_WATER', 3641717, '원/월', '2024-01-01', NULL);

-- [표40] 시설물보험료
INSERT INTO md_expense_item (scenario_id, exp_code, exp_name, group_code, sort_order, is_active)
VALUES ('default', 'PASS_FACILITY_INS', '시설물보험료', 'PASSTHROUGH', 2200, 1);
INSERT INTO md_expense_pricebook (scenario_id, exp_code, unit_price, unit, effective_from, effective_to)
VALUES ('default', 'PASS_FACILITY_INS', 5832292, '원/월', '2024-01-01', NULL);
