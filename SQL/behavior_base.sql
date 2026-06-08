CREATE TABLE behavior_base AS
SELECT
    ROW_NUMBER() OVER (
        ORDER BY user_id, item_id, time, behavior_type
    ) AS sample_id,
    user_id,
    item_id,
    item_category,
    behavior_type AS current_behavior_type,
    datetime(time || ':00:00') AS sample_time
FROM user_behavior_raw;