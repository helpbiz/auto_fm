-- 노무비에서 이미 계산되는 인적보험료 7개 항목은 세부 경비 입력 불필요.
-- 해당 exp_code의 세부 데이터가 있으면 제거하여 DB를 일치시킨다.
DELETE FROM md_expense_sub_item
WHERE exp_code IN (
  'FIX_INS_INDUST',   -- 산재보험료
  'FIX_INS_PENSION',  -- 국민연금
  'FIX_INS_EMPLOY',   -- 고용보험료
  'FIX_INS_HEALTH',   -- 국민건강보험료
  'FIX_INS_LONGTERM', -- 노인장기요양보험료
  'FIX_INS_WAGE',     -- 임금채권보장보험료
  'FIX_INS_ASBESTOS'  -- 석면피해구제분담금
);
