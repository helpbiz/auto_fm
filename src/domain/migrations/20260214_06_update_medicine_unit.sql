-- 의약품비 단위 'SET/월' → 'SET/년' (수량 = 연간 SET, 저장·계산 시 입력값÷12÷합계인원)
UPDATE md_expense_sub_item
SET unit = 'SET/년'
WHERE exp_code = 'FIX_WEL_MEDICINE' AND unit = 'SET/월';
