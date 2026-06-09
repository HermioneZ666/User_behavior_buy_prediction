DROP TABLE IF EXISTS feature_table;

CREATE TABLE feature_table AS
SELECT
    b.sample_id,
    b.user_id,
    b.item_id,
    b.item_category,
    b.current_behavior_type,
    b.sample_time,

    uf.user_pv_cnt_7d,
    uf.user_fav_cnt_7d,
    uf.user_cart_cnt_7d,
    uf.user_buy_cnt_7d,
    uf.user_total_behavior_7d,
    uf.user_active_days_7d,
    uf.user_buy_rate_7d,
    uf.user_cart_rate_7d,
    uf.user_fav_rate_7d,

    itf.item_pv_cnt_7d,
    itf.item_fav_cnt_7d,
    itf.item_cart_cnt_7d,
    itf.item_buy_cnt_7d,
    itf.item_total_behavior_7d,
    itf.item_unique_user_7d,
    itf.item_buy_rate_7d,
    itf.item_cart_rate_7d,

    cf.cate_pv_cnt_7d,
    cf.cate_fav_cnt_7d,
    cf.cate_cart_cnt_7d,
    cf.cate_buy_cnt_7d,
    cf.cate_total_behavior_7d,
    cf.cate_buy_rate_7d,
    cf.cate_cart_rate_7d,

    uif.ui_pv_cnt_7d,
    uif.ui_fav_cnt_7d,
    uif.ui_cart_cnt_7d,
    uif.ui_buy_cnt_7d,
    uif.ui_total_behavior_7d,
    uif.ui_buy_rate_7d,
    uif.ui_cart_rate_7d,
    uif.ui_has_fav_7d,
    uif.ui_has_cart_7d,
    uif.ui_has_buy_7d,

    ucf.uc_pv_cnt_7d,
    ucf.uc_fav_cnt_7d,
    ucf.uc_cart_cnt_7d,
    ucf.uc_buy_cnt_7d,
    ucf.uc_total_behavior_7d,
    ucf.uc_buy_rate_7d,

    tf.hour,
    tf.weekday,
    tf.is_weekend,
    tf.is_night,

    utf.user_night_behavior_cnt_7d,
    utf.user_weekend_behavior_cnt_7d,
    utf.user_night_ratio_7d,
    utf.user_weekend_ratio_7d,

    itemtf.item_night_behavior_cnt_7d,
    itemtf.item_weekend_behavior_cnt_7d,
    itemtf.item_night_buy_cnt_7d,
    itemtf.item_weekend_buy_cnt_7d,
    itemtf.item_night_ratio_7d,
    itemtf.item_weekend_ratio_7d,
    itemtf.item_night_buy_ratio_7d,
    itemtf.item_weekend_buy_ratio_7d,

    catetf.cate_night_behavior_cnt_7d,
    catetf.cate_weekend_behavior_cnt_7d,
    catetf.cate_night_buy_cnt_7d,
    catetf.cate_weekend_buy_cnt_7d,
    catetf.cate_night_ratio_7d,
    catetf.cate_weekend_ratio_7d,
    catetf.cate_night_buy_ratio_7d,
    catetf.cate_weekend_buy_ratio_7d,

    tgf.user_last_action_gap_hour,
    tgf.ui_last_action_gap_hour,
    tgf.uc_last_action_gap_hour,

    l.label

FROM behavior_base b

LEFT JOIN user_features uf
    ON b.sample_id = uf.sample_id

LEFT JOIN item_features itf
    ON b.sample_id = itf.sample_id

LEFT JOIN category_features cf
    ON b.sample_id = cf.sample_id

LEFT JOIN user_item_features uif
    ON b.sample_id = uif.sample_id

LEFT JOIN user_category_features ucf
    ON b.sample_id = ucf.sample_id

LEFT JOIN time_features tf
    ON b.sample_id = tf.sample_id

LEFT JOIN user_time_features utf
    ON b.sample_id = utf.sample_id

LEFT JOIN item_time_features itemtf
    ON b.sample_id = itemtf.sample_id

LEFT JOIN category_time_features catetf
    ON b.sample_id = catetf.sample_id

LEFT JOIN time_gap_features tgf
    ON b.sample_id = tgf.sample_id

LEFT JOIN label_table l
    ON b.sample_id = l.sample_id;