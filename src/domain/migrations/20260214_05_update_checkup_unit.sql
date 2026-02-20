-- 건강검진비 단위 '회/월' → '회/년' (수량은 연간 지급수량, 저장·계산 시 ÷12 적용)
UPDATE md_expense_sub_item
SET unit = '회/년'
WHERE exp_code = 'FIX_WEL_CHECKUP' AND unit = '회/월';
