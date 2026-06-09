DROP TABLE IF EXISTS label_table;
CREATE TABLE label_table AS
SELECT
    s.sample_id,

    CASE
        WHEN EXISTS (
            SELECT 1
            FROM behavior_base b
            WHERE b.user_id = s.user_id
              AND b.item_id = s.item_id
              AND b.current_behavior_type = 4
              AND b.sample_time > s.sample_time
              AND b.sample_time <= datetime(s.sample_time, '+1 day')
        )
        THEN 1
        ELSE 0
    END AS label

FROM behavior_base s;