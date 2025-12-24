# Netflix Media Content Provider — Logical Data Model

_Detailed dimension and fact table specifications for BigQuery implementation_

---

## Table of Contents

1. [Requirements Verification](#requirements-verification)
2. [Dimension Tables](#dimension-tables)
3. [Fact Tables](#fact-tables)
4. [Service Columns Standard](#service-columns-standard)

---

## Requirements Verification

### ✅ Business Case Coverage

| #  | Requirement (Ukrainian)                      | Requirement (English)                    | Covered By                                                     | Status |
|:---|:---------------------------------------------|:-----------------------------------------|:---------------------------------------------------------------|:------:|
| 1  | Підписки з набором телеканалів та фільмів    | Subscriptions with TV channels and movies| dim_plan, fact_subscription_event                              | ✅     |
| 2  | Строки 1, 3, 12, 24 місяці з вартістю        | Terms 1, 3, 12, 24 months with pricing   | dim_term, price_amount in fact                                 | ✅     |
| 3  | Ваучери за 1 грн з інформацією про покупця   | 1 UAH vouchers with buyer info           | fact_voucher_sale, dim_prospect                                | ✅     |
| 4  | Партнерство з магазинами ТВ (3 міс підписка) | TV store partnership (3 mo subscription) | fact_subscription_event + promotion_type=TV_BUNDLE             | ✅     |
| 5  | Перегляд ТВ каналів та контенту              | Watch TV channels and content            | fact_viewing_session, dim_content                              | ✅     |
| 6  | Купівля/оренда фільмів з правовласниками     | Buy/rent movies with rights holders      | fact_content_tx, dim_rights_holder                             | ✅     |
| 7  | Сервіси в інших країнах                      | International services                   | dim_geography (country, region, city)                          | ✅     |
| 8  | До 5 пристроїв на підписку                   | Up to 5 devices per subscription         | fact_device_link, dim_device                                   | ✅     |
| 9  | Сімейний профіль + додаткові профілі         | Family profile + additional profiles     | dim_profile (is_family_default, demographics)                  | ✅     |
| 10 | "Приведи друга" піраміда (50/5 грн)          | Refer-a-friend pyramid (50/5 UAH)        | fact_referral_edge, fact_referral_bonus_tx, dim_referral_depth | ✅     |

### ✅ Analytical Requirements Coverage

| Department    | Requirement                                              | Fact Table(s)                                       | Key Measures/Fields                                       | Status |
|:--------------|:---------------------------------------------------------|:----------------------------------------------------|:----------------------------------------------------------|:------:|
| **Sales**     | Subscription signups by plan, term, users, geography     | subscription_event                                  | signup_count, price_amount, plan_key, term_key, geo_key   | ✅     |
| **Sales**     | Active subscriptions monthly by region                   | subscription_monthly_snapshot                       | active_subscriptions, active_flag, geo_key                | ✅     |
| **Sales**     | Movies purchased/rented with rights holder linkage       | content_tx                                          | tx_count, gross_amount, royalty_amount, rights_holder_key | ✅     |
| **Sales**     | Plan change trends (upgrades/downgrades/non-renewal)     | plan_change                                         | change_count, from_plan_key, to_plan_key, churn_flag      | ✅     |
| **Marketing** | Voucher distribution by stores and prospects             | voucher_sale                                        | voucher_sale_count, partner_store_key, prospect_key       | ✅     |
| **Marketing** | Voucher conversion & lag analysis                        | voucher_lifecycle                                   | is_activated_flag, is_converted_flag, lag_days            | ✅     |
| **Marketing** | Refer-a-friend efficiency                                | referral_edge, referral_bonus_tx                    | referral_count, bonus_amount, depth_key                   | ✅     |
| **Marketing** | Partner store productivity (TV bundle)                   | subscription_event (promotion_type filter)          | signup_count, partner_store_key                           | ✅     |
| **Marketing** | Under-served regions vs demographics                     | region_demographics + subscription_monthly_snapshot | population, active_subscriptions, penetration_rate        | ✅     |  
| **Product**   | Most demanded content (watch time)                       | viewing_session                                     | watch_seconds, session_count, content_key                 | ✅     |
| **Product**   | User demographics × content × device × time              | viewing_session + dim_profile                       | profile demographics, device_key, time_key                | ✅     |
| **Fraud**     | Simultaneous multi-location streaming detection          | viewing_session                                     | start_ts, end_ts, geo_key, profile_key                    | ✅     |

**Result: ALL 12 analytical requirements are covered ✅**

---

## Dimension Tables

### dim_date

| Column                 | Data Type   | Key | SCD  | Description                      |
|:-----------------------|:------------|:----|:-----|:---------------------------------|
| date_key               | INT64       | PK  | —    | Surrogate key (YYYYMMDD format)  |
| calendar_date          | DATE        | BK  | —    | Natural key                      |
| — _Attributes_         | —           | —   | —    | —                                |
| year                   | INT64       |     | SCD1 | Calendar year                    |
| quarter                | INT64       |     | SCD1 | Quarter (1-4)                    |
| month                  | INT64       |     | SCD1 | Month (1-12)                     |
| month_name             | STRING      |     | SCD1 | Month name (January, etc.)       |
| day                    | INT64       |     | SCD1 | Day of month                     |
| day_of_week            | INT64       |     | SCD1 | Day of week (1=Mon, 7=Sun)       |
| day_name               | STRING      |     | SCD1 | Day name (Monday, etc.)          |
| week_of_year           | INT64       |     | SCD1 | ISO week number                  |
| is_weekend             | BOOL        |     | SCD1 | Weekend flag                     |
| is_holiday             | BOOL        |     | SCD1 | Holiday flag (country-specific)  |
| month_start_flag       | BOOL        |     | SCD1 | First day of month               |
| month_end_flag         | BOOL        |     | SCD1 | Last day of month                |
| — _Service Columns_    | —           | —   | —    | —                                |
| etl_inserted_ts        | TIMESTAMP   |     | —    | Record insert timestamp          |
| etl_updated_ts         | TIMESTAMP   |     | —    | Record update timestamp          |
| etl_batch_id           | STRING      |     | —    | ETL batch identifier             |

---

### dim_time

| Column                 | Data Type   | Key | SCD  | Description                      |
|:-----------------------|:------------|:----|:-----|:---------------------------------|
| time_key               | INT64       | PK  | —    | Surrogate key (HHMMSS format)    |
| hhmmss                 | STRING      | BK  | —    | Time string HH:MM:SS             |
| — _Attributes_         | —           | —   | —    | —                                |
| hour                   | INT64       |     | SCD1 | Hour (0-23)                      |
| minute                 | INT64       |     | SCD1 | Minute (0-59)                    |
| second                 | INT64       |     | SCD1 | Second (0-59)                    |
| day_part               | STRING      |     | SCD1 | Morning/Afternoon/Evening/Night  |
| hour_band              | STRING      |     | SCD1 | Hour range (00-06, 06-12, etc.)  |
| is_prime_time          | BOOL        |     | SCD1 | Prime time flag (19:00-23:00)    |
| — _Service Columns_    | —           | —   | —    | —                                |
| etl_inserted_ts        | TIMESTAMP   |     | —    | Record insert timestamp          |
| etl_batch_id           | STRING      |     | —    | ETL batch identifier             |

---

### dim_user

| Column                 | Data Type   | Key | SCD  | Description                          |
|:-----------------------|:------------|:----|:-----|:-------------------------------------|
| user_key               | INT64       | PK  | —    | Surrogate key                        |
| user_id                | STRING      | BK  | —    | Business key (account ID)            |
| — _SCD2 Tracking_      | —           | —   | —    | —                                    |
| effective_start_ts     | TIMESTAMP   |     | SCD2 | Version start timestamp              |
| effective_end_ts       | TIMESTAMP   |     | SCD2 | Version end timestamp (NULL=current) |
| is_current             | BOOL        |     | SCD2 | Current version flag                 |
| — _Attributes_         | —           | —   | —    | —                                    |
| email_hash             | STRING      |     | SCD1 | Hashed email for privacy             |
| phone_hash             | STRING      |     | SCD1 | Hashed phone for privacy             |
| signup_date_key        | INT64       |     | SCD1 | FK to dim_date (signup date)         |
| signup_channel         | STRING      |     | SCD1 | Organic/Referral/Partner/Voucher     |
| current_geo_key        | INT64       |     | SCD2 | FK to dim_geography (current)        |
| account_status         | STRING      |     | SCD2 | Active/Suspended/Closed              |
| preferred_language     | STRING      |     | SCD2 | User's preferred language            |
| — _Service Columns_    | —           | —   | —    | —                                    |
| etl_inserted_ts        | TIMESTAMP   |     | —    | Record insert timestamp              |
| etl_updated_ts         | TIMESTAMP   |     | —    | Record update timestamp              |
| etl_batch_id           | STRING      |     | —    | ETL batch identifier                 |
| hash_data_scd1         | STRING      |     | —    | Hash of SCD1 columns                 |
| hash_data_scd2         | STRING      |     | —    | Hash of SCD2 columns                 |

---

### dim_profile

| Column                 | Data Type   | Key | SCD  | Description                              |
|:-----------------------|:------------|:----|:-----|:-----------------------------------------|
| profile_key            | INT64       | PK  | —    | Surrogate key                            |
| profile_id             | STRING      | BK  | —    | Business key (profile ID)                |
| user_id                | STRING      |     | —    | Parent user account                      |
| — _SCD2 Tracking_      | —           | —   | —    | —                                        |
| effective_start_ts     | TIMESTAMP   |     | SCD2 | Version start timestamp                  |
| effective_end_ts       | TIMESTAMP   |     | SCD2 | Version end timestamp                    |
| is_current             | BOOL        |     | SCD2 | Current version flag                     |
| — _Attributes_         | —           | —   | —    | —                                        |
| profile_name           | STRING      |     | SCD2 | Profile display name                     |
| age_band               | STRING      |     | SCD2 | Age group (0-12/13-17/18-34/35-54/55+)   |
| gender                 | STRING      |     | SCD2 | Male/Female/Other/Unknown                |
| habitual_city          | STRING      |     | SCD2 | Usual city of residence                  |
| is_family_default      | BOOL        |     | SCD1 | Default family profile flag              |
| avatar_id              | STRING      |     | SCD2 | Profile avatar identifier                |
| maturity_rating        | STRING      |     | SCD2 | Content maturity level                   |
| — _Service Columns_    | —           | —   | —    | —                                        |
| etl_inserted_ts        | TIMESTAMP   |     | —    | Record insert timestamp                  |
| etl_updated_ts         | TIMESTAMP   |     | —    | Record update timestamp                  |
| etl_batch_id           | STRING      |     | —    | ETL batch identifier                     |
| hash_data_scd2         | STRING      |     | —    | Hash of SCD2 columns                     |

---

### dim_geography

| Column                 | Data Type   | Key | SCD  | Description                              |
|:-----------------------|:------------|:----|:-----|:-----------------------------------------|
| geo_key                | INT64       | PK  | —    | Surrogate key                            |
| geo_code               | STRING      | BK  | —    | Composite key (country+region+city codes)|
| — _Attributes_         | —           | —   | —    | —                                        |
| country_code           | STRING      |     | SCD1 | ISO country code (UA, PL, etc.)          |
| country                | STRING      |     | SCD1 | Country name                             |
| region_code            | STRING      |     | SCD1 | Region/oblast code                       |
| region                 | STRING      |     | SCD1 | Region name                              |
| city_code              | STRING      |     | SCD1 | City code                                |
| city                   | STRING      |     | SCD1 | City name                                |
| latitude_bucket        | STRING      |     | SCD1 | Latitude range for fraud detection       |
| longitude_bucket       | STRING      |     | SCD1 | Longitude range for fraud detection      |
| timezone               | STRING      |     | SCD1 | Timezone (Europe/Kyiv, etc.)             |
| population_band        | STRING      |     | SCD1 | City size band                           |
| — _Service Columns_    | —           | —   | —    | —                                        |
| etl_inserted_ts        | TIMESTAMP   |     | —    | Record insert timestamp                  |
| etl_updated_ts         | TIMESTAMP   |     | —    | Record update timestamp                  |
| etl_batch_id           | STRING      |     | —    | ETL batch identifier                     |

---

### dim_plan

| Column                 | Data Type   | Key | SCD  | Description                              |
|:-----------------------|:------------|:----|:-----|:-----------------------------------------|
| plan_key               | INT64       | PK  | —    | Surrogate key                            |
| plan_code              | STRING      | BK  | —    | Business key (plan code)                 |
| — _SCD2 Tracking_      | —           | —   | —    | —                                        |
| effective_start_ts     | TIMESTAMP   |     | SCD2 | Version start timestamp                  |
| effective_end_ts       | TIMESTAMP   |     | SCD2 | Version end timestamp                    |
| is_current             | BOOL        |     | SCD2 | Current version flag                     |
| — _Attributes_         | —           | —   | —    | —                                        |
| plan_name              | STRING      |     | SCD2 | Plan display name                        |
| plan_tier              | STRING      |     | SCD2 | Basic/Standard/Premium                   |
| included_channels_cnt  | INT64       |     | SCD2 | Number of TV channels                    |
| included_titles_cnt    | INT64       |     | SCD2 | Number of movies/shows                   |
| max_streams            | INT64       |     | SCD2 | Max concurrent streams                   |
| max_resolution         | STRING      |     | SCD2 | SD/HD/4K                                 |
| base_price_monthly     | NUMERIC     |     | SCD2 | Base monthly price                       |
| is_active              | BOOL        |     | SCD2 | Plan available for sale                  |
| — _Service Columns_    | —           | —   | —    | —                                        |
| etl_inserted_ts        | TIMESTAMP   |     | —    | Record insert timestamp                  |
| etl_updated_ts         | TIMESTAMP   |     | —    | Record update timestamp                  |
| etl_batch_id           | STRING      |     | —    | ETL batch identifier                     |
| hash_data_scd2         | STRING      |     | —    | Hash of SCD2 columns                     |

---

### dim_term

| Column                 | Data Type   | Key | SCD  | Description                              |
|:-----------------------|:------------|:----|:-----|:-----------------------------------------|
| term_key               | INT64       | PK  | —    | Surrogate key                            |
| term_months            | INT64       | BK  | SCD1 | Term length: 1, 3, 12, 24                |
| — _Attributes_         | —           | —   | —    | —                                        |
| term_name              | STRING      |     | SCD1 | Monthly/Quarterly/Annual/Biennial        |
| discount_pct           | NUMERIC     |     | SCD1 | Discount for longer terms                |
| is_promo_eligible      | BOOL        |     | SCD1 | Can be used with promotions              |
| — _Service Columns_    | —           | —   | —    | —                                        |
| etl_inserted_ts        | TIMESTAMP   |     | —    | Record insert timestamp                  |
| etl_batch_id           | STRING      |     | —    | ETL batch identifier                     |

---

### dim_device

| Column                 | Data Type   | Key | SCD  | Description                              |
|:-----------------------|:------------|:----|:-----|:-----------------------------------------|
| device_key             | INT64       | PK  | —    | Surrogate key                            |
| device_id              | STRING      | BK  | —    | Device unique identifier                 |
| — _Attributes_         | —           | —   | —    | —                                        |
| device_type            | STRING      |     | SCD1 | SmartTV/Mobile/Tablet/PC/STB             |
| manufacturer           | STRING      |     | SCD1 | Samsung/LG/Apple/etc.                    |
| model                  | STRING      |     | SCD1 | Device model                             |
| os                     | STRING      |     | SCD1 | Operating system                         |
| os_version             | STRING      |     | SCD1 | OS version                               |
| app_version            | STRING      |     | SCD1 | Netflix app version                      |
| screen_resolution      | STRING      |     | SCD1 | Screen resolution                        |
| — _Service Columns_    | —           | —   | —    | —                                        |
| etl_inserted_ts        | TIMESTAMP   |     | —    | Record insert timestamp                  |
| etl_updated_ts         | TIMESTAMP   |     | —    | Record update timestamp                  |
| etl_batch_id           | STRING      |     | —    | ETL batch identifier                     |

---

### dim_content

| Column                      | Data Type   | Key | SCD  | Description                              |
|:----------------------------|:------------|:----|:-----|:-----------------------------------------|
| content_key                 | INT64       | PK  | —    | Surrogate key                            |
| content_id                  | STRING      | BK  | —    | Content identifier                       |
| — _SCD2 Tracking (optional)_ | —          | —   | —    | —                                        |
| effective_start_ts          | TIMESTAMP   |     | SCD2 | Version start (for metadata changes)     |
| effective_end_ts            | TIMESTAMP   |     | SCD2 | Version end                              |
| is_current                  | BOOL        |     | SCD2 | Current version flag                     |
| — _Attributes_              | —           | —   | —    | —                                        |
| title                       | STRING      |     | SCD2 | Content title                            |
| original_title              | STRING      |     | SCD1 | Original language title                  |
| content_type                | STRING      |     | SCD1 | Movie/TVShow/TVChannel/Documentary       |
| genre                       | STRING      |     | SCD2 | Primary genre                            |
| genres_all                  | STRING      |     | SCD2 | All genres (comma-separated)             |
| release_year                | INT64       |     | SCD1 | Year of release                          |
| duration_minutes            | INT64       |     | SCD1 | Duration (movies)                        |
| seasons_count               | INT64       |     | SCD2 | Number of seasons (shows)                |
| episodes_count              | INT64       |     | SCD2 | Number of episodes (shows)               |
| maturity_rating             | STRING      |     | SCD1 | Age rating (PG/PG-13/R/etc.)             |
| country_of_origin           | STRING      |     | SCD1 | Production country                       |
| rights_holder_key           | INT64       |     | SCD2 | FK to dim_rights_holder                  |
| is_included_in_subscription | BOOL        |     | SCD2 | Part of subscription or pay-per-view     |
| — _Service Columns_         | —           | —   | —    | —                                        |
| etl_inserted_ts             | TIMESTAMP   |     | —    | Record insert timestamp                  |
| etl_updated_ts              | TIMESTAMP   |     | —    | Record update timestamp                  |
| etl_batch_id                | STRING      |     | —    | ETL batch identifier                     |
| hash_data_scd2              | STRING      |     | —    | Hash of SCD2 columns                     |

---

### dim_rights_holder

| Column                 | Data Type   | Key | SCD  | Description                              |
|:-----------------------|:------------|:----|:-----|:-----------------------------------------|
| rights_holder_key      | INT64       | PK  | —    | Surrogate key                            |
| rights_holder_id       | STRING      | BK  | —    | Rights holder identifier                 |
| — _Attributes_         | —           | —   | —    | —                                        |
| name                   | STRING      |     | SCD1 | Company/studio name                      |
| contract_type          | STRING      |     | SCD1 | Exclusive/Non-exclusive/Revenue-share    |
| royalty_pct            | NUMERIC     |     | SCD1 | Royalty percentage                       |
| country                | STRING      |     | SCD1 | Headquarters country                     |
| contact_email          | STRING      |     | SCD1 | Contact email                            |
| contract_start_date    | DATE        |     | SCD1 | Contract start                           |
| contract_end_date      | DATE        |     | SCD1 | Contract end                             |
| — _Service Columns_    | —           | —   | —    | —                                        |
| etl_inserted_ts        | TIMESTAMP   |     | —    | Record insert timestamp                  |
| etl_updated_ts         | TIMESTAMP   |     | —    | Record update timestamp                  |
| etl_batch_id           | STRING      |     | —    | ETL batch identifier                     |

---

### dim_partner_store

| Column                 | Data Type   | Key | SCD  | Description                              |
|:-----------------------|:------------|:----|:-----|:-----------------------------------------|
| partner_store_key      | INT64       | PK  | —    | Surrogate key                            |
| store_id               | STRING      | BK  | —    | Store identifier                         |
| — _Attributes_         | —           | —   | —    | —                                        |
| store_name             | STRING      |     | SCD1 | Store display name                       |
| chain                  | STRING      |     | SCD1 | Retail chain (Comfy/Foxtrot/etc.)        |
| store_type             | STRING      |     | SCD1 | Electronics/Hypermarket/Online           |
| address                | STRING      |     | SCD1 | Store address                            |
| geo_key                | INT64       |     | SCD1 | FK to dim_geography                      |
| opening_date           | DATE        |     | SCD1 | Store opening date                       |
| is_active              | BOOL        |     | SCD1 | Currently active partner                 |
| — _Service Columns_    | —           | —   | —    | —                                        |
| etl_inserted_ts        | TIMESTAMP   |     | —    | Record insert timestamp                  |
| etl_updated_ts         | TIMESTAMP   |     | —    | Record update timestamp                  |
| etl_batch_id           | STRING      |     | —    | ETL batch identifier                     |

---

### dim_promotion

| Column                 | Data Type   | Key | SCD  | Description                                  |
|:-----------------------|:------------|:----|:-----|:---------------------------------------------|
| promotion_key          | INT64       | PK  | —    | Surrogate key                                |
| promotion_code         | STRING      | BK  | —    | Promotion code                               |
| — _Attributes_         | —           | —   | —    | —                                            |
| promotion_type         | STRING      |     | SCD1 | VOUCHER/TV_BUNDLE/REFERRAL/SEASONAL/NONE     |
| promotion_name         | STRING      |     | SCD1 | Promotion display name                       |
| description            | STRING      |     | SCD1 | Promotion description                        |
| discount_pct           | NUMERIC     |     | SCD1 | Discount percentage                          |
| discount_amount        | NUMERIC     |     | SCD1 | Fixed discount amount                        |
| start_date             | DATE        |     | SCD1 | Promotion start date                         |
| end_date               | DATE        |     | SCD1 | Promotion end date                           |
| is_active              | BOOL        |     | SCD1 | Currently active                             |
| — _Service Columns_    | —           | —   | —    | —                                            |
| etl_inserted_ts        | TIMESTAMP   |     | —    | Record insert timestamp                      |
| etl_updated_ts         | TIMESTAMP   |     | —    | Record update timestamp                      |
| etl_batch_id           | STRING      |     | —    | ETL batch identifier                         |

---

### dim_payment_method

| Column                 | Data Type   | Key | SCD  | Description                              |
|:-----------------------|:------------|:----|:-----|:-----------------------------------------|
| payment_method_key     | INT64       | PK  | —    | Surrogate key                            |
| payment_method_code    | STRING      | BK  | —    | Payment method code                      |
| — _Attributes_         | —           | —   | —    | —                                        |
| payment_type           | STRING      |     | SCD1 | Card/Wallet/Bank/Crypto                  |
| provider               | STRING      |     | SCD1 | Visa/Mastercard/PrivatPay/etc.           |
| provider_country       | STRING      |     | SCD1 | Provider country                         |
| is_active              | BOOL        |     | SCD1 | Currently accepted                       |
| — _Service Columns_    | —           | —   | —    | —                                        |
| etl_inserted_ts        | TIMESTAMP   |     | —    | Record insert timestamp                  |
| etl_batch_id           | STRING      |     | —    | ETL batch identifier                     |

---

### dim_currency

| Column                 | Data Type   | Key | SCD  | Description                              |
|:-----------------------|:------------|:----|:-----|:-----------------------------------------|
| currency_key           | INT64       | PK  | —    | Surrogate key                            |
| iso_currency_code      | STRING      | BK  | —    | ISO 4217 code (UAH, EUR, USD)            |
| — _Attributes_         | —           | —   | —    | —                                        |
| currency_name          | STRING      |     | SCD1 | Currency full name                       |
| symbol                 | STRING      |     | SCD1 | Currency symbol (₴, €, $)                |
| decimal_places         | INT64       |     | SCD1 | Decimal precision                        |
| — _Service Columns_    | —           | —   | —    | —                                        |
| etl_inserted_ts        | TIMESTAMP   |     | —    | Record insert timestamp                  |
| etl_batch_id           | STRING      |     | —    | ETL batch identifier                     |

---

### dim_voucher

| Column                 | Data Type   | Key | SCD  | Description                              |
|:-----------------------|:------------|:----|:-----|:-----------------------------------------|
| voucher_key            | INT64       | PK  | —    | Surrogate key                            |
| voucher_code           | STRING      | BK  | —    | Unique voucher code                      |
| — _Attributes_         | —           | —   | —    | —                                        |
| voucher_type           | STRING      |     | SCD1 | TRIAL_1UAH/GIFT/PROMO                    |
| nominal_term_months    | INT64       |     | SCD1 | Voucher term (usually 1 month)           |
| nominal_value          | NUMERIC     |     | SCD1 | Voucher face value                       |
| generated_date         | DATE        |     | SCD1 | When voucher was generated               |
| expiry_date            | DATE        |     | SCD1 | Voucher expiration date                  |
| — _Service Columns_    | —           | —   | —    | —                                        |
| etl_inserted_ts        | TIMESTAMP   |     | —    | Record insert timestamp                  |
| etl_batch_id           | STRING      |     | —    | ETL batch identifier                     |

---

### dim_referral_depth

| Column                 | Data Type   | Key | SCD  | Description                              |
|:-----------------------|:------------|:----|:-----|:-----------------------------------------|
| depth_key              | INT64       | PK  | —    | Surrogate key                            |
| depth                  | INT64       | BK  | —    | Referral depth level                     |
| — _Attributes_         | —           | —   | —    | —                                        |
| depth_name             | STRING      |     | SCD1 | Direct (1) / Indirect (2+)               |
| bonus_amount           | NUMERIC     |     | SCD1 | Standard bonus (50 or 5 UAH)             |
| depth_description      | STRING      |     | SCD1 | Description of level                     |
| — _Service Columns_    | —           | —   | —    | —                                        |
| etl_inserted_ts        | TIMESTAMP   |     | —    | Record insert timestamp                  |
| etl_batch_id           | STRING      |     | —    | ETL batch identifier                     |

---

### dim_status

| Column                 | Data Type   | Key | SCD  | Description                                  |
|:-----------------------|:------------|:----|:-----|:---------------------------------------------|
| status_key             | INT64       | PK  | —    | Surrogate key                                |
| status_code            | STRING      | BK  | —    | Status code                                  |
| — _Attributes_         | —           | —   | —    | —                                            |
| status_name            | STRING      |     | SCD1 | Status display name                          |
| status_group           | STRING      |     | SCD1 | SUBSCRIPTION/VOUCHER/PLAYBACK/DEVICE/PROFILE |
| status_order           | INT64       |     | SCD1 | Sort order within group                      |
| is_active_status       | BOOL        |     | SCD1 | Represents active state                      |
| — _Service Columns_    | —           | —   | —    | —                                            |
| etl_inserted_ts        | TIMESTAMP   |     | —    | Record insert timestamp                      |
| etl_batch_id           | STRING      |     | —    | ETL batch identifier                         |

---

### dim_prospect

| Column                 | Data Type   | Key | SCD  | Description                              |
|:-----------------------|:------------|:----|:-----|:-----------------------------------------|
| prospect_key           | INT64       | PK  | —    | Surrogate key                            |
| lead_id                | STRING      | BK  | —    | Lead identifier                          |
| — _SCD2 Tracking_      | —           | —   | —    | —                                        |
| effective_start_ts     | TIMESTAMP   |     | SCD2 | Version start                            |
| effective_end_ts       | TIMESTAMP   |     | SCD2 | Version end                              |
| is_current             | BOOL        |     | SCD2 | Current version flag                     |
| — _Attributes_         | —           | —   | —    | —                                        |
| phone_hash             | STRING      |     | SCD1 | Hashed phone number                      |
| age_band               | STRING      |     | SCD2 | Age group at voucher sale                |
| gender                 | STRING      |     | SCD2 | Male/Female/Unknown                      |
| city_at_sale           | STRING      |     | SCD1 | City when voucher sold                   |
| geo_key                | INT64       |     | SCD1 | FK to dim_geography                      |
| converted_to_user_key  | INT64       |     | SCD2 | FK to dim_user if converted              |
| — _Service Columns_    | —           | —   | —    | —                                        |
| etl_inserted_ts        | TIMESTAMP   |     | —    | Record insert timestamp                  |
| etl_updated_ts         | TIMESTAMP   |     | —    | Record update timestamp                  |
| etl_batch_id           | STRING      |     | —    | ETL batch identifier                     |
| hash_data_scd2         | STRING      |     | —    | Hash of SCD2 columns                     |

---

## Fact Tables

### subscription_event

**Grain:** 1 row per subscription purchase/activation event

| Column                 | Data Type   | Role      | Description                              |
|:-----------------------|:------------|:----------|:-----------------------------------------|
| subscription_event_id  | STRING      | PK        | Surrogate/UUID key                       |
| subscription_id        | STRING      | DD        | Degenerate dimension - subscription ID   |
| contract_id            | STRING      | DD        | Degenerate dimension - contract ID       |
| — _Date/Time_          | —           | —         | —                                        |
| event_date             | DATE        | Partition | Event date for partitioning              |
| event_date_key         | INT64       | FK        | → dim_date                               |
| — _Dimensions_         | —           | —         | —                                        |
| user_key               | INT64       | FK        | → dim_user                               |
| geo_key                | INT64       | FK        | → dim_geography                          |
| plan_key               | INT64       | FK        | → dim_plan                               |
| term_key               | INT64       | FK        | → dim_term                               |
| partner_store_key      | INT64       | FK        | → dim_partner_store (nullable)           |
| promotion_key          | INT64       | FK        | → dim_promotion (nullable)               |
| payment_method_key     | INT64       | FK        | → dim_payment_method (nullable)          |
| currency_key           | INT64       | FK        | → dim_currency                           |
| voucher_key            | INT64       | FK        | → dim_voucher (nullable)                 |
| status_key             | INT64       | FK        | → dim_status                             |
| — _Measures_           | —           | —         | —                                        |
| signup_count           | INT64       | Measure   | Always 1 (fully additive)                |
| price_amount           | NUMERIC     | Measure   | Gross amount charged (fully additive)    |
| discount_amount        | NUMERIC     | Measure   | Discount applied (fully additive)        |
| net_amount             | NUMERIC     | Measure   | Net amount (fully additive)              |
| months_purchased       | INT64       | Measure   | Term in months (semi-additive)           |
| — _Service Columns_    | —           | —         | —                                        |
| etl_inserted_ts        | TIMESTAMP   | —         | Record insert timestamp                  |
| etl_batch_id           | STRING      | —         | ETL batch identifier                     |

---

### subscription_monthly_snapshot

**Grain:** 1 row per user per month per subscription (as-of month start)

**Type:** Periodic Snapshot

| Column                 | Data Type   | Role      | Description                              |
|:-----------------------|:------------|:----------|:-----------------------------------------|
| snapshot_id            | STRING      | PK        | Surrogate key                            |
| subscription_id        | STRING      | DD        | Degenerate dimension                     |
| — _Date_               | —           | —         | —                                        |
| snapshot_month_start   | DATE        | Partition | Month start date for partitioning        |
| month_start_date_key   | INT64       | FK        | → dim_date                               |
| — _Dimensions_         | —           | —         | —                                        |
| user_key               | INT64       | FK        | → dim_user                               |
| geo_key                | INT64       | FK        | → dim_geography                          |
| plan_key               | INT64       | FK        | → dim_plan                               |
| term_key               | INT64       | FK        | → dim_term                               |
| status_key             | INT64       | FK        | → dim_status                             |
| — _Measures_           | —           | —         | —                                        |
| active_flag            | BOOL        | Measure   | Is subscription active (semi-additive)   |
| active_subscriptions   | INT64       | Measure   | Count = 1 (semi-additive)                |
| mrr_amount             | NUMERIC     | Measure   | Monthly recurring revenue (semi-additive)|
| tenure_months          | INT64       | Measure   | Months since signup (non-additive)       |
| — _Service Columns_    | —           | —         | —                                        |
| etl_inserted_ts        | TIMESTAMP   | —         | Record insert timestamp                  |
| etl_batch_id           | STRING      | —         | ETL batch identifier                     |

---

### plan_change

**Grain:** 1 row per plan change (upgrade/downgrade/cancel/non-renewal)

| Column                 | Data Type   | Role      | Description                              |
|:-----------------------|:------------|:----------|:-----------------------------------------|
| plan_change_id         | STRING      | PK        | Surrogate key                            |
| subscription_id        | STRING      | DD        | Degenerate dimension                     |
| — _Date_               | —           | —         | —                                        |
| change_date            | DATE        | Partition | Change date for partitioning             |
| change_date_key        | INT64       | FK        | → dim_date                               |
| — _Dimensions_         | —           | —         | —                                        |
| user_key               | INT64       | FK        | → dim_user                               |
| geo_key                | INT64       | FK        | → dim_geography                          |
| from_plan_key          | INT64       | FK        | → dim_plan (role-playing: from)          |
| to_plan_key            | INT64       | FK        | → dim_plan (role-playing: to)            |
| device_key             | INT64       | FK        | → dim_device (nullable)                  |
| promotion_key          | INT64       | FK        | → dim_promotion (nullable)               |
| status_key             | INT64       | FK        | → dim_status (change reason)             |
| — _Measures_           | —           | —         | —                                        |
| change_count           | INT64       | Measure   | Always 1 (fully additive)                |
| delta_mrr              | NUMERIC     | Measure   | MRR change amount (fully additive)       |
| churn_flag             | BOOL        | Measure   | Is churn/cancellation (non-additive)     |
| — _Service Columns_    | —           | —         | —                                        |
| etl_inserted_ts        | TIMESTAMP   | —         | Record insert timestamp                  |
| etl_batch_id           | STRING      | —         | ETL batch identifier                     |

---

### voucher_sale

**Grain:** 1 row per voucher sold at distribution point

| Column                 | Data Type   | Role      | Description                              |
|:-----------------------|:------------|:----------|:-----------------------------------------|
| voucher_sale_id        | STRING      | PK        | Surrogate key                            |
| voucher_code           | STRING      | DD        | Degenerate dimension                     |
| — _Date_               | —           | —         | —                                        |
| sale_date              | DATE        | Partition | Sale date for partitioning               |
| sale_date_key          | INT64       | FK        | → dim_date                               |
| — _Dimensions_         | —           | —         | —                                        |
| prospect_key           | INT64       | FK        | → dim_prospect                           |
| geo_key                | INT64       | FK        | → dim_geography                          |
| partner_store_key      | INT64       | FK        | → dim_partner_store                      |
| voucher_key            | INT64       | FK        | → dim_voucher                            |
| promotion_key          | INT64       | FK        | → dim_promotion                          |
| — _Measures_           | —           | —         | —                                        |
| voucher_sale_count     | INT64       | Measure   | Always 1 (fully additive)                |
| voucher_price_amount   | NUMERIC     | Measure   | Price paid = 1 UAH (fully additive)      |
| — _Service Columns_    | —           | —         | —                                        |
| etl_inserted_ts        | TIMESTAMP   | —         | Record insert timestamp                  |
| etl_batch_id           | STRING      | —         | ETL batch identifier                     |

---

### voucher_lifecycle

**Grain:** 1 row per voucher, updated at milestones (sale → activation → conversion)

**Type:** Accumulating Snapshot

| Column                            | Data Type   | Role      | Description                                    |
|:----------------------------------|:------------|:----------|:-----------------------------------------------|
| voucher_key                       | INT64       | PK/FK     | → dim_voucher (also PK)                        |
| voucher_code                      | STRING      | DD        | Degenerate dimension                           |
| — _Milestone Dates_               | —           | —         | —                                              |
| sale_date                         | DATE        | Partition | Sale date                                      |
| sale_date_key                     | INT64       | FK        | → dim_date (role-playing)                      |
| activation_date                   | DATE        | —         | Activation date (NULL until activated)         |
| activation_date_key               | INT64       | FK        | → dim_date (role-playing)                      |
| conversion_date                   | DATE        | —         | Conversion date (NULL until converted)         |
| conversion_date_key               | INT64       | FK        | → dim_date (role-playing)                      |
| — _Dimensions_                    | —           | —         | —                                              |
| prospect_key                      | INT64       | FK        | → dim_prospect                                 |
| geo_key                           | INT64       | FK        | → dim_geography                                |
| partner_store_key                 | INT64       | FK        | → dim_partner_store                            |
| promotion_key                     | INT64       | FK        | → dim_promotion                                |
| status_key                        | INT64       | FK        | → dim_status (current state)                   |
| converted_subscription_id         | STRING      | DD        | Subscription ID if converted                   |
| — _Measures_                      | —           | —         | —                                              |
| lag_sale_to_activation_days       | INT64       | Measure   | Days from sale to activation (non-additive)    |
| lag_activation_to_conversion_days | INT64       | Measure   | Days from activation to conversion (non-additive) |
| is_activated_flag                 | BOOL        | Measure   | Has been activated (semi-additive)             |
| is_converted_flag                 | BOOL        | Measure   | Has converted to subscription (semi-additive)  |
| — _Service Columns_               | —           | —         | —                                              |
| etl_inserted_ts                   | TIMESTAMP   | —         | Record insert timestamp                        |
| etl_updated_ts                    | TIMESTAMP   | —         | Record update timestamp                        |
| etl_batch_id                      | STRING      | —         | ETL batch identifier                           |

---

### viewing_session

**Grain:** 1 row per playback session (user-profile-content)

| Column                 | Data Type   | Role      | Description                                  |
|:-----------------------|:------------|:----------|:---------------------------------------------|
| session_id             | STRING      | PK/DD     | Degenerate dimension / PK                    |
| — _Timestamps_         | —           | —         | —                                            |
| start_ts               | TIMESTAMP   | —         | Session start timestamp                      |
| end_ts                 | TIMESTAMP   | —         | Session end timestamp                        |
| start_date             | DATE        | Partition | Start date for partitioning                  |
| start_date_key         | INT64       | FK        | → dim_date                                   |
| start_time_key         | INT64       | FK        | → dim_time                                   |
| — _Dimensions_         | —           | —         | —                                            |
| user_key               | INT64       | FK        | → dim_user                                   |
| profile_key            | INT64       | FK        | → dim_profile                                |
| geo_key                | INT64       | FK        | → dim_geography (session location)           |
| plan_key               | INT64       | FK        | → dim_plan (optional)                        |
| device_key             | INT64       | FK        | → dim_device                                 |
| content_key            | INT64       | FK        | → dim_content                                |
| status_key             | INT64       | FK        | → dim_status (playback status)               |
| — _Measures_           | —           | —         | —                                            |
| watch_seconds          | INT64       | Measure   | Duration in seconds (fully additive)         |
| session_count          | INT64       | Measure   | Always 1 (fully additive)                    |
| concurrent_stream_flag | BOOL        | Measure   | Part of concurrent streaming (for fraud)     |
| — _Service Columns_    | —           | —         | —                                            |
| etl_inserted_ts        | TIMESTAMP   | —         | Record insert timestamp                      |
| etl_batch_id           | STRING      | —         | ETL batch identifier                         |

---

### content_tx

**Grain:** 1 row per content purchase or rental transaction

| Column                 | Data Type   | Role      | Description                              |
|:-----------------------|:------------|:----------|:-----------------------------------------|
| tx_id                  | STRING      | PK/DD     | Transaction ID / PK                      |
| — _Timestamps_         | —           | —         | —                                        |
| tx_ts                  | TIMESTAMP   | —         | Transaction timestamp                    |
| tx_date                | DATE        | Partition | Transaction date                         |
| tx_date_key            | INT64       | FK        | → dim_date                               |
| tx_time_key            | INT64       | FK        | → dim_time                               |
| — _Dimensions_         | —           | —         | —                                        |
| user_key               | INT64       | FK        | → dim_user                               |
| profile_key            | INT64       | FK        | → dim_profile                            |
| geo_key                | INT64       | FK        | → dim_geography                          |
| device_key             | INT64       | FK        | → dim_device                             |
| content_key            | INT64       | FK        | → dim_content                            |
| rights_holder_key      | INT64       | FK        | → dim_rights_holder                      |
| promotion_key          | INT64       | FK        | → dim_promotion (nullable)               |
| payment_method_key     | INT64       | FK        | → dim_payment_method                     |
| currency_key           | INT64       | FK        | → dim_currency                           |
| status_key             | INT64       | FK        | → dim_status (purchase/rental)           |
| — _Measures_           | —           | —         | —                                        |
| tx_count               | INT64       | Measure   | Always 1 (fully additive)                |
| gross_amount           | NUMERIC     | Measure   | Gross transaction amount (fully additive)|
| net_amount             | NUMERIC     | Measure   | Net after fees (fully additive)          |
| royalty_amount         | NUMERIC     | Measure   | Royalty to rights holder (fully additive)|
| — _Service Columns_    | —           | —         | —                                        |
| etl_inserted_ts        | TIMESTAMP   | —         | Record insert timestamp                  |
| etl_batch_id           | STRING      | —         | ETL batch identifier                     |

---

### referral_edge

**Grain:** 1 row per direct referral (referrer → referred friend)

**Type:** Factless Fact

| Column                 | Data Type   | Role      | Description                              |
|:-----------------------|:------------|:----------|:-----------------------------------------|
| edge_id                | STRING      | PK        | Surrogate key                            |
| — _Date_               | —           | —         | —                                        |
| referral_date          | DATE        | Partition | Referral date                            |
| referral_date_key      | INT64       | FK        | → dim_date                               |
| — _Dimensions_         | —           | —         | —                                        |
| referrer_user_key      | INT64       | FK        | → dim_user (role-playing: referrer)      |
| referred_user_key      | INT64       | FK        | → dim_user (role-playing: referred)      |
| promotion_key          | INT64       | FK        | → dim_promotion                          |
| — _Measures_           | —           | —         | —                                        |
| referral_count         | INT64       | Measure   | Always 1 (fully additive, factless)      |
| — _Service Columns_    | —           | —         | —                                        |
| etl_inserted_ts        | TIMESTAMP   | —         | Record insert timestamp                  |
| etl_batch_id           | STRING      | —         | ETL batch identifier                     |

---

### referral_bonus_tx

**Grain:** 1 row per bonus payout event (50 UAH direct, 5 UAH indirect)

| Column                 | Data Type   | Role      | Description                              |
|:-----------------------|:------------|:----------|:-----------------------------------------|
| bonus_tx_id            | STRING      | PK        | Surrogate key                            |
| — _Date_               | —           | —         | —                                        |
| bonus_date             | DATE        | Partition | Bonus payout date                        |
| bonus_date_key         | INT64       | FK        | → dim_date                               |
| — _Dimensions_         | —           | —         | —                                        |
| beneficiary_user_key   | INT64       | FK        | → dim_user (receives bonus)              |
| originating_user_key   | INT64       | FK        | → dim_user (caused the bonus)            |
| depth_key              | INT64       | FK        | → dim_referral_depth                     |
| promotion_key          | INT64       | FK        | → dim_promotion                          |
| currency_key           | INT64       | FK        | → dim_currency                           |
| — _Measures_           | —           | —         | —                                        |
| bonus_count            | INT64       | Measure   | Always 1 (fully additive)                |
| bonus_amount           | NUMERIC     | Measure   | 50 or 5 UAH (fully additive)             |
| — _Service Columns_    | —           | —         | —                                        |
| etl_inserted_ts        | TIMESTAMP   | —         | Record insert timestamp                  |
| etl_batch_id           | STRING      | —         | ETL batch identifier                     |

---

### device_link

**Grain:** 1 row per user-device link/unlink event

**Type:** Factless Fact

| Column                 | Data Type   | Role      | Description                              |
|:-----------------------|:------------|:----------|:-----------------------------------------|
| link_event_id          | STRING      | PK        | Surrogate key                            |
| — _Date_               | —           | —         | —                                        |
| event_date             | DATE        | Partition | Event date                               |
| event_date_key         | INT64       | FK        | → dim_date                               |
| — _Dimensions_         | —           | —         | —                                        |
| user_key               | INT64       | FK        | → dim_user                               |
| device_key             | INT64       | FK        | → dim_device                             |
| status_key             | INT64       | FK        | → dim_status (LINKED/UNLINKED)           |
| — _Measures_           | —           | —         | —                                        |
| link_count             | INT64       | Measure   | Always 1 (fully additive, factless)      |
| — _Service Columns_    | —           | —         | —                                        |
| etl_inserted_ts        | TIMESTAMP   | —         | Record insert timestamp                  |
| etl_batch_id           | STRING      | —         | ETL batch identifier                     |

---

### profile_event

**Grain:** 1 row per profile create/update event

**Type:** Factless Fact

| Column                 | Data Type   | Role      | Description                              |
|:-----------------------|:------------|:----------|:-----------------------------------------|
| profile_event_id       | STRING      | PK        | Surrogate key                            |
| — _Date_               | —           | —         | —                                        |
| event_date             | DATE        | Partition | Event date                               |
| event_date_key         | INT64       | FK        | → dim_date                               |
| — _Dimensions_         | —           | —         | —                                        |
| user_key               | INT64       | FK        | → dim_user                               |
| profile_key            | INT64       | FK        | → dim_profile                            |
| geo_key                | INT64       | FK        | → dim_geography                          |
| status_key             | INT64       | FK        | → dim_status (CREATED/UPDATED)           |
| — _Measures_           | —           | —         | —                                        |
| profile_event_count    | INT64       | Measure   | Always 1 (fully additive, factless)      |
| — _Service Columns_    | —           | —         | —                                        |
| etl_inserted_ts        | TIMESTAMP   | —         | Record insert timestamp                  |
| etl_batch_id           | STRING      | —         | ETL batch identifier                     |

---

### region_demographics

**Grain:** 1 row per region per year (public demographic data)

**Type:** Periodic Snapshot (external data)

| Column                   | Data Type   | Role      | Description                                  |
|:-------------------------|:------------|:----------|:---------------------------------------------|
| record_id                | STRING      | PK        | Surrogate key                                |
| — _Date_                 | —           | —         | —                                            |
| year_date                | DATE        | Partition | Year start date                              |
| year_date_key            | INT64       | FK        | → dim_date                                   |
| — _Dimensions_           | —           | —         | —                                            |
| geo_key                  | INT64       | FK        | → dim_geography (region level)               |
| status_key               | INT64       | FK        | → dim_status (data source version)           |
| — _Measures_             | —           | —         | —                                            |
| population               | INT64       | Measure   | Total population (semi-additive)             |
| target_demo_population   | INT64       | Measure   | Target demographic population (semi-additive)|
| households_count         | INT64       | Measure   | Number of households (semi-additive)         |
| internet_penetration_pct | NUMERIC     | Measure   | % with internet (non-additive)               |
| — _Derived (in queries)_ | —           | —         | —                                            |
| penetration_rate         | NUMERIC     | Derived   | active_subscriptions / population            |
| — _Service Columns_      | —           | —         | —                                            |
| etl_inserted_ts          | TIMESTAMP   | —         | Record insert timestamp                      |
| etl_batch_id             | STRING      | —         | ETL batch identifier                         |

---

## Service Columns Standard

All dimension and fact tables include standard ETL service columns:

| Column           | Data Type   | Description                            | Required In                               |
|:-----------------|:------------|:---------------------------------------|:------------------------------------------|
| etl_inserted_ts  | TIMESTAMP   | When record was first inserted         | All tables                                |
| etl_updated_ts   | TIMESTAMP   | When record was last updated           | SCD2 dimensions, accumulating snapshots   |
| etl_batch_id     | STRING      | ETL batch/job identifier               | All tables                                |
| hash_data_scd1   | STRING      | MD5/SHA hash of SCD1 columns           | SCD2 dimensions (for change detection)    |
| hash_data_scd2   | STRING      | MD5/SHA hash of SCD2 columns           | SCD2 dimensions (for change detection)    |

---

## Summary

| Category         | Count | Tables                                                                                                                                                                                                            |
|:-----------------|:-----:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Dimensions**   |  16   | date, time, user, profile, geography, plan, term, device, content, rights_holder, partner_store, promotion, payment_method, currency, voucher, referral_depth, status, prospect                                   |
| **Facts**        |  12   | subscription_event, subscription_monthly_snapshot, plan_change, voucher_sale, voucher_lifecycle, viewing_session, content_tx, referral_edge, referral_bonus_tx, device_link, profile_event, region_demographics   |
| **Total Tables** |  28   |                                                                                                                                                                                                                   |

**All 12 analytical requirements from the home task are fully covered.**

---

_Generated from Netflix Bus Matrix Logical Data Model_
