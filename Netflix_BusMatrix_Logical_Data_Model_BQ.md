# Netflix Bus Matrix → Logical Data Model (BigQuery)


## Requirements Coverage

| Area      | Analytical requirement                                                                                           | Covered by fact process(es)                                 | Key measures / fields                                                                     | Notes                                                                    |
|:----------|:-----------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------|:------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------|
| Sales     | Subscription signups by plan, term (1/3/12/24), users, geography                                                 | Subscription Purchase/Activation                            | signup_count, price_amount, term_months, plan_key, geography_key                          | Includes paid, voucher-converted, and partner TV bundle subscriptions    |
| Sales     | Active subscriptions at the beginning of each month by region                                                    | Subscription Monthly Snapshot                               | active_flag, active_subscriptions, snapshot_month_key, geography_key                      | Periodic snapshot at month-start (or month grain)                        |
| Sales     | Movies purchased/rented over time with rights holder linkage                                                     | Content Purchase/Rental                                     | purchase_count/rental_count, gross_amount, royalty_amount, rights_holder_key, content_key | Royalty can be stored or derived from contract %                         |
| Sales     | Plan change trend: upgrades/downgrades/non-renewals by month                                                     | Plan Change Event; Subscription Monthly Snapshot            | change_count, from_plan_key, to_plan_key, change_reason, month_key                        | Non-renewal captured as churn/cancel event                               |
| Marketing | Voucher distribution volumes by distribution points and prospect profiles                                        | Voucher Sale                                                | voucher_sale_count, voucher_price, store_key, prospect_demographics                       | Prospect is a pre-customer/lead dimension                                |
| Marketing | Voucher conversion: in activation now, converted to subscription, lags sale→activation and activation→conversion | Voucher Lifecycle (Accumulating)                            | status, sale_date, activation_date, conversion_date, lag_days                             | Accumulating snapshot supports lags as milestone differences             |
| Marketing | Refer-a-friend efficiency: number of friends, bonus payouts, top referrers                                       | Referral Edge; Referral Bonus Tx                            | direct_referrals_count, bonus_amount, depth, referrer_user_key                            | Variable-depth hierarchy handled via closure/path and bonus transactions |
| Marketing | Partner store productivity: promo subscriptions with TV purchase                                                 | Subscription Purchase/Activation (promotion_type=TV_BUNDLE) | signup_count, promotion_key, partner_store_key                                            | Can be filtered by promotion type                                        |
| Marketing | Under-served regions: user adoption % vs region demographics (open data)                                         | Region Demographics Snapshot; Subscription Monthly Snapshot | population, target_demo_population, active_subscriptions                                  | Public demographics loaded as separate snapshot by region/year           |
| Product   | Most demanded content: watch time by content/channel/title                                                       | Content Viewing Session                                     | watch_seconds, session_count, content_key                                                 | Can be extended to minute grain if needed                                |
| Product   | Which users (demographics) watch what content, on which devices, and time of day                                 | Content Viewing Session; Profile Dimension                  | watch_seconds, device_key, time_key, profile_age_band, profile_gender                     | Time-of-day analysis via time dimension or time attributes               |
| Fraud     | Detect abuse: one profile consuming content simultaneously from many geolocations                                | Content Viewing Session                                     | session_start_ts, session_end_ts, geo_key, profile_key                                    | Overlap detection uses session intervals + geo                           |

## Dimensions Dictionary

| Dimension          | Surrogate Key      | Natural/Business Key      | SCD Type          | Key attributes (examples)                             | Notes                                                 |
|:-------------------|:-------------------|:--------------------------|:------------------|:------------------------------------------------------|:------------------------------------------------------|
| dim_date           | date_key           | calendar_date             | Type 1            | year, month, day, month_start_flag                    | Role-playing via multiple FKs in facts                |
| dim_time           | time_key           | hhmmss                    | Type 1            | hour, minute, day_part                                | Used for time-of-day analysis                         |
| dim_user           | user_key           | user_id                   | Type 2 (hybrid)   | signup_channel, current_geo, email_hash               | History for moving geography/demographics if required |
| dim_profile        | profile_key        | profile_id                | Type 2            | age_band, gender, habitual_city, is_family_default    | Needed for per-profile analytics & fraud              |
| dim_geography      | geo_key            | country/region/city codes | Type 1            | country, region, city, latitude_bucket                | Supports multi-country expansion                      |
| dim_plan           | plan_key           | plan_code                 | Type 2            | plan_name, included_channels_cnt, included_titles_cnt | Price can be stored in plan or fact                   |
| dim_term           | term_key           | term_months               | Type 1            | 1, 3, 12, 24                                          | Small static dimension                                |
| dim_device         | device_key         | device_id                 | Type 1            | device_type, os, app_version                          | Up to 5 devices per subscription/account              |
| dim_content        | content_key        | content_id                | Type 2 (optional) | title, content_type, genre, release_year              | Covers movies, shows, TV channels                     |
| dim_rights_holder  | rights_holder_key  | rights_holder_id          | Type 1            | name, contract_type                                   | Royalty % may be separate bridge/contract table       |
| dim_partner_store  | partner_store_key  | store_id                  | Type 1            | store_name, chain, location                           | TV retailers and distribution points                  |
| dim_promotion      | promotion_key      | promotion_code            | Type 1            | promotion_type (VOUCHER/TV_BUNDLE/REFERRAL)           | Used across multiple facts                            |
| dim_payment_method | payment_method_key | payment_method_code       | Type 1            | card/wallet/bank, provider                            |                                                       |
| dim_currency       | currency_key       | iso_currency_code         | Type 1            | code, name                                            | Store transaction + standardized amounts where needed |
| dim_voucher        | voucher_key        | voucher_code              | Type 1            | voucher_type, nominal_term_months                     | Voucher code can also be a degenerate dimension       |
| dim_referral_depth | depth_key          | depth                     | Type 1            | depth=1 direct, depth>=2 indirect                     | Supports pyramid rewards                              |
| dim_status         | status_key         | status_code               | Type 1            | subscription_status, voucher_status                   | Often implemented as a junk dimension                 |
| dim_prospect       | prospect_key       | lead_id/phone_hash        | Type 2 (optional) | age_band, gender, city_at_sale                        | Used for voucher buyers before account creation       |

## Bus Matrix (Full)

| Business process                            | Grain                                             | Fact table                         | Key measures (examples)                                                                                     | Date   | Time   | User   | Profile   | Prospect   | Geography   | Plan   | Term   | Device   | Content   | Rights Holder   | Partner Store   | Voucher   | Promotion   | Payment Method   | Currency   | Referral Depth   | Status   |
|:--------------------------------------------|:--------------------------------------------------|:-----------------------------------|:------------------------------------------------------------------------------------------------------------|:-------|:-------|:-------|:----------|:-----------|:------------|:-------|:-------|:---------|:----------|:----------------|:----------------|:----------|:------------|:-----------------|:-----------|:-----------------|:---------|
| Subscription Purchase/Activation            | 1 row per subscription contract/purchase event    | fact_subscription_event            | signup_count, price_amount, discount_amount, months_purchased                                               | X      |        | X      |           |            | X           | X      | X      |          |           |                 | X               | X         | X           | X                | X          |                  | X        |
| Subscription Monthly Snapshot (month-start) | 1 row per user per month per active subscription  | fact_subscription_monthly_snapshot | active_flag, active_subscriptions, mrr_amount, tenure_months                                                | X      |        | X      |           |            | X           | X      | X      |          |           |                 |                 |           |             |                  |            |                  | X        |
| Plan Change Event                           | 1 row per plan change per user                    | fact_plan_change                   | change_count, delta_mrr, churn_flag                                                                         | X      |        | X      |           |            | X           | X      |        | X        |           |                 |                 |           | X           |                  |            |                  | X        |
| Voucher Sale (1 UAH vouchers)               | 1 row per voucher sold                            | fact_voucher_sale                  | voucher_sale_count, voucher_price=1                                                                         | X      |        |        |           | X          | X           |        |        |          |           |                 | X               | X         | X           |                  |            |                  |          |
| Voucher Lifecycle (Accumulating)            | 1 row per voucher (updated at milestones)         | fact_voucher_lifecycle             | sale_date, activation_date, conversion_date, lag_sale_to_activation_days, lag_activation_to_conversion_days | X      |        |        |           | X          | X           |        |        |          |           |                 | X               | X         | X           |                  |            |                  | X        |
| Content Viewing Session                     | 1 row per playback session (user-profile-content) | fact_viewing_session               | watch_seconds, session_count, concurrent_stream_flag                                                        | X      | X      | X      | X         |            | X           | X      |        | X        | X         |                 |                 |           |             |                  |            |                  | X        |
| Content Purchase/Rental                     | 1 row per purchase or rental transaction          | fact_content_tx                    | tx_count, gross_amount, net_amount, royalty_amount                                                          | X      | X      | X      | X         |            | X           |        |        | X        | X         | X               |                 |           | X           | X                | X          |                  | X        |
| Referral Edge (direct friend link)          | 1 row per direct referral relationship            | fact_referral_edge                 | referral_count (factless=1)                                                                                 | X      |        | X      |           |            |             |        |        |          |           |                 |                 |           | X           |                  |            |                  |          |
| Referral Bonus Transactions                 | 1 row per bonus payout event                      | fact_referral_bonus_tx             | bonus_amount, bonus_count                                                                                   | X      |        | X      |           |            |             |        |        |          |           |                 |                 |           | X           |                  | X          | X                |          |
| Device Linking (up to 5 devices)            | 1 row per user-device link event                  | fact_device_link                   | link_count (factless=1)                                                                                     | X      |        | X      |           |            |             |        |        | X        |           |                 |                 |           |             |                  |            |                  | X        |
| Profile Creation/Update (factless)          | 1 row per profile create/update event             | fact_profile_event                 | profile_event_count (1)                                                                                     | X      |        | X      | X         |            | X           |        |        |          |           |                 |                 |           |             |                  |            |                  | X        |
| Region Demographics Snapshot (public data)  | 1 row per region per year (or month)              | fact_region_demographics           | population, target_demo_population, penetration_rate (derived)                                              | X      |        |        |           |            | X           |        |        |          |           |                 |                 |           |             |                  |            |                  | X        |

## Star_Subscription_Event

| FACT TABLE                  | fact_subscription_event                                                                     | Unnamed: 2                              | Unnamed: 3                  |
|:----------------------------|:--------------------------------------------------------------------------------------------|:----------------------------------------|:----------------------------|
| Grain                       | 1 row per subscription purchase/activation (incl. renewals, voucher conversions, TV bundle) |                                         |                             |
| Degenerate dimensions / IDs | subscription_id (DD), contract_id (DD)                                                      |                                         |                             |
| Fact fields (logical)       | Type (BigQuery)                                                                             | Key role                                | Description                 |
| subscription_event_id       | STRING                                                                                      | PK (surrogate or UUID)                  | Unique event record         |
| event_date_key              | INT64                                                                                       | FK                                      | Date of purchase/activation |
| user_key                    | INT64                                                                                       | FK                                      | Customer account            |
| geo_key                     | INT64                                                                                       | FK                                      | Geography at event          |
| plan_key                    | INT64                                                                                       | FK                                      | Plan at start               |
| term_key                    | INT64                                                                                       | FK                                      | Term (months)               |
| partner_store_key           | INT64                                                                                       | FK                                      | Retail partner (optional)   |
| promotion_key               | INT64                                                                                       | FK                                      | Promotion type (optional)   |
| payment_method_key          | INT64                                                                                       | FK                                      | Payment method (optional)   |
| currency_key                | INT64                                                                                       | FK                                      | Currency                    |
| voucher_key                 | INT64                                                                                       | FK                                      | Voucher (optional)          |
| status_key                  | INT64                                                                                       | FK                                      | Status at event             |
| price_amount                | NUMERIC                                                                                     | Measure                                 | Gross charged amount        |
| discount_amount             | NUMERIC                                                                                     | Measure                                 | Discount applied            |
| months_purchased            | INT64                                                                                       | Measure                                 | Term length in months       |
| Dimensions                  | FK field (in fact)                                                                          | Notes                                   |                             |
| dim_date                    | event_date_key                                                                              | role-playing: purchase/activation date  |                             |
| dim_user                    | user_key                                                                                    |                                         |                             |
| dim_geography               | geo_key                                                                                     | geo as-of event                         |                             |
| dim_plan                    | plan_key                                                                                    |                                         |                             |
| dim_term                    | term_key                                                                                    | 1/3/12/24 months                        |                             |
| dim_partner_store           | partner_store_key                                                                           | nullable; TV retailers / voucher points |                             |
| dim_promotion               | promotion_key                                                                               | VOUCHER/TV_BUNDLE/REFERRAL/None         |                             |
| dim_payment_method          | payment_method_key                                                                          | nullable for free promos                |                             |
| dim_currency                | currency_key                                                                                |                                         |                             |
| dim_voucher                 | voucher_key                                                                                 | nullable; if originated from voucher    |                             |
| dim_status                  | status_key                                                                                  | subscription status at event            |                             |
| Measures                    | Additivity                                                                                  | Notes                                   |                             |
| signup_count                | Fully additive                                                                              | Usually constant 1                      |                             |
| price_amount                | Fully additive                                                                              | Transaction amount in currency          |                             |
| discount_amount             | Fully additive                                                                              |                                         |                             |
| months_purchased            | Additive across users, not across time                                                      | Often treated as informational          |                             |

## Star_Subscription_Snapshot

| FACT TABLE                  | fact_subscription_monthly_snapshot                            | Unnamed: 2                          | Unnamed: 3                  |
|:----------------------------|:--------------------------------------------------------------|:------------------------------------|:----------------------------|
| Grain                       | 1 row per user per month per subscription (as-of month start) |                                     |                             |
| Degenerate dimensions / IDs | subscription_id (DD)                                          |                                     |                             |
| Fact fields (logical)       | Type (BigQuery)                                               | Key role                            | Description                 |
| snapshot_id                 | STRING                                                        | PK                                  | Unique snapshot record      |
| month_start_date_key        | INT64                                                         | FK                                  | Snapshot date (month start) |
| user_key                    | INT64                                                         | FK                                  |                             |
| geo_key                     | INT64                                                         | FK                                  |                             |
| plan_key                    | INT64                                                         | FK                                  |                             |
| term_key                    | INT64                                                         | FK                                  |                             |
| status_key                  | INT64                                                         | FK                                  |                             |
| active_flag                 | BOOL                                                          | Measure                             |                             |
| active_subscriptions        | INT64                                                         | Measure                             | Typically 1                 |
| mrr_amount                  | NUMERIC                                                       | Measure                             | Monthly recurring revenue   |
| tenure_months               | INT64                                                         | Measure                             | Months since start          |
| Dimensions                  | FK field (in fact)                                            | Notes                               |                             |
| dim_date                    | month_start_date_key                                          | Month start snapshot date           |                             |
| dim_user                    | user_key                                                      |                                     |                             |
| dim_geography               | geo_key                                                       |                                     |                             |
| dim_plan                    | plan_key                                                      |                                     |                             |
| dim_term                    | term_key                                                      |                                     |                             |
| dim_status                  | status_key                                                    | active/canceled/etc.                |                             |
| Measures                    | Additivity                                                    | Notes                               |                             |
| active_flag                 | Semi-additive                                                 | Not additive across time            |                             |
| active_subscriptions        | Semi-additive                                                 | Count=1; use as-of aggregation      |                             |
| mrr_amount                  | Semi-additive                                                 | Not summed across time without care |                             |
| tenure_months               | Non-additive                                                  | Use avg/percentiles                 |                             |

## Star_Plan_Change

| FACT TABLE                  | fact_plan_change                                           | Unnamed: 2                         | Unnamed: 3   |
|:----------------------------|:-----------------------------------------------------------|:-----------------------------------|:-------------|
| Grain                       | 1 row per plan change (upgrade/downgrade/cancel/non-renew) |                                    |              |
| Degenerate dimensions / IDs | subscription_id (DD)                                       |                                    |              |
| Fact fields (logical)       | Type (BigQuery)                                            | Key role                           | Description  |
| plan_change_id              | STRING                                                     | PK                                 |              |
| change_date_key             | INT64                                                      | FK                                 |              |
| user_key                    | INT64                                                      | FK                                 |              |
| geo_key                     | INT64                                                      | FK                                 |              |
| from_plan_key               | INT64                                                      | FK                                 |              |
| to_plan_key                 | INT64                                                      | FK                                 |              |
| device_key                  | INT64                                                      | FK                                 |              |
| promotion_key               | INT64                                                      | FK                                 |              |
| status_key                  | INT64                                                      | FK                                 | Reason       |
| delta_mrr                   | NUMERIC                                                    | Measure                            |              |
| change_count                | INT64                                                      | Measure                            | 1            |
| churn_flag                  | BOOL                                                       | Measure                            |              |
| Dimensions                  | FK field (in fact)                                         | Notes                              |              |
| dim_date                    | change_date_key                                            |                                    |              |
| dim_user                    | user_key                                                   |                                    |              |
| dim_geography               | geo_key                                                    |                                    |              |
| dim_plan                    | from_plan_key / to_plan_key                                | Two role-playing references        |              |
| dim_device                  | device_key                                                 | Optional; channel of change        |              |
| dim_promotion               | promotion_key                                              | Optional                           |              |
| dim_status                  | status_key                                                 | Change reason/status               |              |
| Measures                    | Additivity                                                 | Notes                              |              |
| change_count                | Fully additive                                             | Constant 1                         |              |
| delta_mrr                   | Fully additive                                             |                                    |              |
| churn_flag                  | Non-additive                                               | Use count distinct churn_flag=true |              |

## Star_Voucher_Sale

| FACT TABLE                  | fact_voucher_sale                            | Unnamed: 2                 | Unnamed: 3   |
|:----------------------------|:---------------------------------------------|:---------------------------|:-------------|
| Grain                       | 1 row per voucher sold at distribution point |                            |              |
| Degenerate dimensions / IDs | voucher_code (DD)                            |                            |              |
| Fact fields (logical)       | Type (BigQuery)                              | Key role                   | Description  |
| voucher_sale_id             | STRING                                       | PK                         |              |
| sale_date_key               | INT64                                        | FK                         |              |
| prospect_key                | INT64                                        | FK                         |              |
| geo_key                     | INT64                                        | FK                         |              |
| partner_store_key           | INT64                                        | FK                         |              |
| voucher_key                 | INT64                                        | FK                         |              |
| promotion_key               | INT64                                        | FK                         |              |
| voucher_sale_count          | INT64                                        | Measure                    | 1            |
| voucher_price_amount        | NUMERIC                                      | Measure                    | 1 UAH        |
| Dimensions                  | FK field (in fact)                           | Notes                      |              |
| dim_date                    | sale_date_key                                |                            |              |
| dim_prospect                | prospect_key                                 | Lead/prospect at sale time |              |
| dim_geography               | geo_key                                      | City/country at sale       |              |
| dim_partner_store           | partner_store_key                            | Distribution point         |              |
| dim_voucher                 | voucher_key                                  |                            |              |
| dim_promotion               | promotion_key                                | Voucher campaign           |              |
| Measures                    | Additivity                                   | Notes                      |              |
| voucher_sale_count          | Fully additive                               | 1                          |              |
| voucher_price_amount        | Fully additive                               | Usually 1 UAH              |              |

## Star_Voucher_Lifecycle

| FACT TABLE                        | fact_voucher_lifecycle                                                    | Unnamed: 2                         | Unnamed: 3               |
|:----------------------------------|:--------------------------------------------------------------------------|:-----------------------------------|:-------------------------|
| Grain                             | 1 row per voucher, updated at milestones (sale → activation → conversion) |                                    |                          |
| Degenerate dimensions / IDs       | voucher_code (DD)                                                         |                                    |                          |
| Fact fields (logical)             | Type (BigQuery)                                                           | Key role                           | Description              |
| voucher_key                       | INT64                                                                     | PK/FK                              | Voucher surrogate key    |
| sale_date_key                     | INT64                                                                     | FK                                 |                          |
| activation_date_key               | INT64                                                                     | FK                                 | Nullable until activated |
| conversion_date_key               | INT64                                                                     | FK                                 | Nullable until converted |
| prospect_key                      | INT64                                                                     | FK                                 |                          |
| geo_key                           | INT64                                                                     | FK                                 |                          |
| partner_store_key                 | INT64                                                                     | FK                                 |                          |
| promotion_key                     | INT64                                                                     | FK                                 |                          |
| status_key                        | INT64                                                                     | FK                                 |                          |
| lag_sale_to_activation_days       | INT64                                                                     | Measure                            | Derived in ETL or query  |
| lag_activation_to_conversion_days | INT64                                                                     | Measure                            |                          |
| is_activated_flag                 | BOOL                                                                      | Measure                            |                          |
| is_converted_flag                 | BOOL                                                                      | Measure                            |                          |
| Dimensions                        | FK field (in fact)                                                        | Notes                              |                          |
| dim_date                          | sale_date_key / activation_date_key / conversion_date_key                 | Role-playing dates                 |                          |
| dim_prospect                      | prospect_key                                                              |                                    |                          |
| dim_geography                     | geo_key                                                                   |                                    |                          |
| dim_partner_store                 | partner_store_key                                                         |                                    |                          |
| dim_voucher                       | voucher_key                                                               |                                    |                          |
| dim_promotion                     | promotion_key                                                             |                                    |                          |
| dim_status                        | status_key                                                                | Issued/Activated/Converted/Expired |                          |
| Measures                          | Additivity                                                                | Notes                              |                          |
| lag_sale_to_activation_days       | Non-additive                                                              | Use avg/percentiles                |                          |
| lag_activation_to_conversion_days | Non-additive                                                              | Use avg/percentiles                |                          |
| is_activated_flag                 | Semi-additive                                                             | As-of counts                       |                          |
| is_converted_flag                 | Semi-additive                                                             | As-of counts                       |                          |

## Star_Viewing_Session

| FACT TABLE                  | fact_viewing_session       | Unnamed: 2                            | Unnamed: 3          |
|:----------------------------|:---------------------------|:--------------------------------------|:--------------------|
| Grain                       | 1 row per playback session |                                       |                     |
| Degenerate dimensions / IDs | session_id (DD)            |                                       |                     |
| Fact fields (logical)       | Type (BigQuery)            | Key role                              | Description         |
| session_id                  | STRING                     | PK (degenerate)                       | Playback session id |
| start_ts                    | TIMESTAMP                  | Attribute                             | Session start       |
| end_ts                      | TIMESTAMP                  | Attribute                             | Session end         |
| start_date_key              | INT64                      | FK                                    |                     |
| start_time_key              | INT64                      | FK                                    |                     |
| user_key                    | INT64                      | FK                                    |                     |
| profile_key                 | INT64                      | FK                                    |                     |
| geo_key                     | INT64                      | FK                                    |                     |
| plan_key                    | INT64                      | FK                                    |                     |
| device_key                  | INT64                      | FK                                    |                     |
| content_key                 | INT64                      | FK                                    |                     |
| status_key                  | INT64                      | FK                                    |                     |
| watch_seconds               | INT64                      | Measure                               |                     |
| session_count               | INT64                      | Measure                               | 1                   |
| Dimensions                  | FK field (in fact)         | Notes                                 |                     |
| dim_date                    | start_date_key             |                                       |                     |
| dim_time                    | start_time_key             |                                       |                     |
| dim_user                    | user_key                   |                                       |                     |
| dim_profile                 | profile_key                |                                       |                     |
| dim_geography               | geo_key                    | Geo at session                        |                     |
| dim_plan                    | plan_key                   | Plan at session (optional, derivable) |                     |
| dim_device                  | device_key                 |                                       |                     |
| dim_content                 | content_key                |                                       |                     |
| dim_status                  | status_key                 | Playback status                       |                     |
| Measures                    | Additivity                 | Notes                                 |                     |
| watch_seconds               | Fully additive             |                                       |                     |
| session_count               | Fully additive             | 1                                     |                     |

## Star_Content_Tx

| FACT TABLE                  | fact_content_tx                      | Unnamed: 2                 | Unnamed: 3   |
|:----------------------------|:-------------------------------------|:---------------------------|:-------------|
| Grain                       | 1 row per content purchase or rental |                            |              |
| Degenerate dimensions / IDs | tx_id (DD)                           |                            |              |
| Fact fields (logical)       | Type (BigQuery)                      | Key role                   | Description  |
| tx_id                       | STRING                               | PK (degenerate)            |              |
| tx_date_key                 | INT64                                | FK                         |              |
| tx_time_key                 | INT64                                | FK                         |              |
| user_key                    | INT64                                | FK                         |              |
| profile_key                 | INT64                                | FK                         |              |
| geo_key                     | INT64                                | FK                         |              |
| device_key                  | INT64                                | FK                         |              |
| content_key                 | INT64                                | FK                         |              |
| rights_holder_key           | INT64                                | FK                         |              |
| promotion_key               | INT64                                | FK                         |              |
| payment_method_key          | INT64                                | FK                         |              |
| currency_key                | INT64                                | FK                         |              |
| status_key                  | INT64                                | FK                         |              |
| gross_amount                | NUMERIC                              | Measure                    |              |
| net_amount                  | NUMERIC                              | Measure                    |              |
| royalty_amount              | NUMERIC                              | Measure                    |              |
| tx_count                    | INT64                                | Measure                    | 1            |
| Dimensions                  | FK field (in fact)                   | Notes                      |              |
| dim_date                    | tx_date_key                          |                            |              |
| dim_time                    | tx_time_key                          |                            |              |
| dim_user                    | user_key                             |                            |              |
| dim_profile                 | profile_key                          |                            |              |
| dim_geography               | geo_key                              |                            |              |
| dim_device                  | device_key                           |                            |              |
| dim_content                 | content_key                          |                            |              |
| dim_rights_holder           | rights_holder_key                    |                            |              |
| dim_promotion               | promotion_key                        | Optional                   |              |
| dim_payment_method          | payment_method_key                   |                            |              |
| dim_currency                | currency_key                         |                            |              |
| dim_status                  | status_key                           | purchase vs rental etc.    |              |
| Measures                    | Additivity                           | Notes                      |              |
| tx_count                    | Fully additive                       | 1                          |              |
| gross_amount                | Fully additive                       |                            |              |
| net_amount                  | Fully additive                       |                            |              |
| royalty_amount              | Fully additive                       | Allocated to rights holder |              |

## Star_Referral_Edge

| FACT TABLE                  | fact_referral_edge                            | Unnamed: 2                 | Unnamed: 3   |
|:----------------------------|:----------------------------------------------|:---------------------------|:-------------|
| Grain                       | 1 row per direct referral (referrer → friend) |                            |              |
| Degenerate dimensions / IDs | edge_id (DD)                                  |                            |              |
| Fact fields (logical)       | Type (BigQuery)                               | Key role                   | Description  |
| edge_id                     | STRING                                        | PK                         |              |
| referral_date_key           | INT64                                         | FK                         |              |
| referrer_user_key           | INT64                                         | FK                         |              |
| referred_user_key           | INT64                                         | FK                         |              |
| promotion_key               | INT64                                         | FK                         |              |
| referral_count              | INT64                                         | Measure                    | 1            |
| Dimensions                  | FK field (in fact)                            | Notes                      |              |
| dim_date                    | referral_date_key                             |                            |              |
| dim_user                    | referrer_user_key / referred_user_key         | Two role-playing user keys |              |
| dim_promotion               | promotion_key                                 | REFERRAL campaign          |              |
| Measures                    | Additivity                                    | Notes                      |              |
| referral_count              | Fully additive                                | 1 (factless)               |              |

## Star_Referral_Bonus

| FACT TABLE                  | fact_referral_bonus_tx                                           | Unnamed: 2                                                   | Unnamed: 3   |
|:----------------------------|:-----------------------------------------------------------------|:-------------------------------------------------------------|:-------------|
| Grain                       | 1 row per bonus payout event (direct=50, indirect=5 by depth>=2) |                                                              |              |
| Degenerate dimensions / IDs | bonus_tx_id (DD)                                                 |                                                              |              |
| Fact fields (logical)       | Type (BigQuery)                                                  | Key role                                                     | Description  |
| bonus_tx_id                 | STRING                                                           | PK                                                           |              |
| bonus_date_key              | INT64                                                            | FK                                                           |              |
| beneficiary_user_key        | INT64                                                            | FK                                                           |              |
| originating_user_key        | INT64                                                            | FK                                                           |              |
| depth_key                   | INT64                                                            | FK                                                           |              |
| promotion_key               | INT64                                                            | FK                                                           |              |
| currency_key                | INT64                                                            | FK                                                           |              |
| bonus_amount                | NUMERIC                                                          | Measure                                                      |              |
| bonus_count                 | INT64                                                            | Measure                                                      | 1            |
| Dimensions                  | FK field (in fact)                                               | Notes                                                        |              |
| dim_date                    | bonus_date_key                                                   |                                                              |              |
| dim_user                    | beneficiary_user_key / originating_user_key                      | Beneficiary receives bonus; originating is downstream signup |              |
| dim_referral_depth          | depth_key                                                        |                                                              |              |
| dim_promotion               | promotion_key                                                    |                                                              |              |
| dim_currency                | currency_key                                                     |                                                              |              |
| Measures                    | Additivity                                                       | Notes                                                        |              |
| bonus_amount                | Fully additive                                                   |                                                              |              |
| bonus_count                 | Fully additive                                                   | 1                                                            |              |

## Star_Device_Link

| FACT TABLE                  | fact_device_link                        | Unnamed: 2      | Unnamed: 3   |
|:----------------------------|:----------------------------------------|:----------------|:-------------|
| Grain                       | 1 row per user-device link/unlink event |                 |              |
| Degenerate dimensions / IDs | link_event_id (DD)                      |                 |              |
| Fact fields (logical)       | Type (BigQuery)                         | Key role        | Description  |
| link_event_id               | STRING                                  | PK              |              |
| event_date_key              | INT64                                   | FK              |              |
| user_key                    | INT64                                   | FK              |              |
| device_key                  | INT64                                   | FK              |              |
| status_key                  | INT64                                   | FK              |              |
| link_count                  | INT64                                   | Measure         | 1            |
| Dimensions                  | FK field (in fact)                      | Notes           |              |
| dim_date                    | event_date_key                          |                 |              |
| dim_user                    | user_key                                |                 |              |
| dim_device                  | device_key                              |                 |              |
| dim_status                  | status_key                              | LINKED/UNLINKED |              |
| Measures                    | Additivity                              | Notes           |              |
| link_count                  | Fully additive                          | 1 (factless)    |              |

## Star_Profile_Event

| FACT TABLE                  | fact_profile_event                    | Unnamed: 2      | Unnamed: 3   |
|:----------------------------|:--------------------------------------|:----------------|:-------------|
| Grain                       | 1 row per profile create/update event |                 |              |
| Degenerate dimensions / IDs | profile_event_id (DD)                 |                 |              |
| Fact fields (logical)       | Type (BigQuery)                       | Key role        | Description  |
| profile_event_id            | STRING                                | PK              |              |
| event_date_key              | INT64                                 | FK              |              |
| user_key                    | INT64                                 | FK              |              |
| profile_key                 | INT64                                 | FK              |              |
| geo_key                     | INT64                                 | FK              |              |
| status_key                  | INT64                                 | FK              |              |
| profile_event_count         | INT64                                 | Measure         | 1            |
| Dimensions                  | FK field (in fact)                    | Notes           |              |
| dim_date                    | event_date_key                        |                 |              |
| dim_user                    | user_key                              |                 |              |
| dim_profile                 | profile_key                           |                 |              |
| dim_geography               | geo_key                               |                 |              |
| dim_status                  | status_key                            | CREATED/UPDATED |              |
| Measures                    | Additivity                            | Notes           |              |
| profile_event_count         | Fully additive                        | 1 (factless)    |              |

## Star_Region_Demographics

| FACT TABLE                  | fact_region_demographics             | Unnamed: 2                                  | Unnamed: 3   |
|:----------------------------|:-------------------------------------|:--------------------------------------------|:-------------|
| Grain                       | 1 row per region per year (or month) |                                             |              |
| Degenerate dimensions / IDs | record_id (DD)                       |                                             |              |
| Fact fields (logical)       | Type (BigQuery)                      | Key role                                    | Description  |
| record_id                   | STRING                               | PK                                          |              |
| year_date_key               | INT64                                | FK                                          |              |
| geo_key                     | INT64                                | FK                                          |              |
| status_key                  | INT64                                | FK                                          |              |
| population                  | INT64                                | Measure                                     |              |
| target_demo_population      | INT64                                | Measure                                     |              |
| Dimensions                  | FK field (in fact)                   | Notes                                       |              |
| dim_date                    | year_date_key                        | Year start date key                         |              |
| dim_geography               | geo_key                              | Region-level geography                      |              |
| dim_status                  | status_key                           | Source/version                              |              |
| Measures                    | Additivity                           | Notes                                       |              |
| population                  | Semi-additive                        | Not additive across time                    |              |
| target_demo_population      | Semi-additive                        |                                             |              |
| penetration_rate            | Non-additive                         | Derived = active_subscriptions / population |              |

## Model Checks

| Check                       | Rule of thumb                                | Status   | Notes                                                                                    |
|:----------------------------|:---------------------------------------------|:---------|:-----------------------------------------------------------------------------------------|
| Grain defined for each fact | Every fact table must declare one grain      | OK       |                                                                                          |
| No mixed-grain facts        | Header measures allocated or separated       | OK       | Header-level subscription amounts modeled as transaction facts; viewing is session grain |
| Conformed dimensions        | Shared dimensions reused across facts        | OK       | Date, User, Geo, Plan, Content, Device are conformed                                     |
| Voucher lags                | Use accumulating snapshot for milestone lags | OK       | Voucher lifecycle fact                                                                   |
| Referral pyramid            | Handle variable-depth hierarchy              | OK       | Bonus tx + depth dim; closure/path in ETL if needed                                      |
| Fraud requirement           | Needs session intervals + geo + profile      | OK       | Viewing session fact includes start/end timestamps                                       |
| Currency conversion rates   | Need exchange rate table for multi-currency  | TODO     | Will need dim_exchange_rate or snapshot fact later                                       |
