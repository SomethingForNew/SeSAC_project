-- 강남3구(송파구11710, 서초구11650, 강남구11680)
select count(*)
from all_data
where "BLDG_USG" = '아파트'
    and (
        "CGG_CD" = 11710
        or "BLDG_USG" = '아파트'
        and "CGG_CD" = 11680
        or "BLDG_USG" = '아파트'
        and "CGG_CD" = 11650
    ) -- select *
    -- from all_data
    -- where "CGG_CD" = 11710;
    -- SELECT column_name
    -- FROM information_schema.columns
    -- WHERE table_name = 'all_data';
    -- select *
    -- from t_temp
    -- where CGG_CD = 11710