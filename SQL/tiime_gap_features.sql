CREATE TABLE time_gap_features AS
SELECT
    s.sample_id,

    (
        CAST(strftime('%s', s.sample_time) AS INTEGER)
        -
        CAST(strftime('%s',
            (
                SELECT MAX(b.sample_time)
                FROM behavior_base b
                WHERE b.user_id = s.user_id
                AND b.sample_time < s.sample_time
            )
        ) AS INTEGER)
    ) / 3600.0
    AS user_last_action_gap_hour,

    (
        CAST(strftime('%s', s.sample_time) AS INTEGER)
        -
        CAST(strftime('%s',
            (
                SELECT MAX(b.sample_time)
                FROM behavior_base b
                WHERE b.user_id = s.user_id
                AND b.item_id = s.item_id
                AND b.sample_time < s.sample_time
            )
        ) AS INTEGER)
    ) / 3600.0
    AS ui_last_action_gap_hour,

    (
        CAST(strftime('%s', s.sample_time) AS INTEGER)
        -
        CAST(strftime('%s',
            (
                SELECT MAX(b.sample_time)
                FROM behavior_base b
                WHERE b.user_id = s.user_id
                AND b.item_category = s.item_category
                AND b.sample_time < s.sample_time
            )
        ) AS INTEGER)
    ) / 3600.0
    AS uc_last_action_gap_hour

FROM behavior_base s;