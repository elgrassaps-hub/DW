# Netflix Data Warehouse — Star Schema Diagrams

_Visual representation of all star schemas from the Bus Matrix Logical Data Model_

---

## Flat Structure Star Schema Examples (Detailed View)

Below are detailed star schemas showing all attributes, similar to a Logical Data Model diagram.

### Example 1: fact_subscription_event (Detailed)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                                                         │
│  ┌─────────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐        │
│  │      dim_date           │      │      dim_user           │      │      dim_plan           │      │      dim_term           │        │
│  ├─────────────────────────┤      ├─────────────────────────┤      ├─────────────────────────┤      ├─────────────────────────┤        │
│  │ PK date_key       INT64 │      │ PK user_key       INT64 │      │ PK plan_key       INT64 │      │ PK term_key       INT64 │        │
│  │ BK calendar_date   DATE │      │ BK user_id       STRING │      │ BK plan_code     STRING │      │ BK term_months    INT64 │        │
│  │ ─────────────────────── │      │ ─────────────────────── │      │ ─────────────────────── │      │ ─────────────────────── │        │
│  │    year           INT64 │      │    email_hash    STRING │      │    plan_name     STRING │      │    term_name     STRING │        │
│  │    quarter        INT64 │      │    signup_channel STRING│      │    plan_tier     STRING │      │    discount_pct NUMERIC │        │
│  │    month          INT64 │      │    current_geo_key INT64│      │    included_     INT64  │      │    is_promo_      BOOL  │        │
│  │    day            INT64 │      │    account_status STRING│      │       channels_cnt      │      │       eligible          │        │
│  │    day_of_week    INT64 │      │ ─── SCD2 ────────────── │      │    included_     INT64  │      │ ─── Service ─────────── │        │
│  │    month_start_flag BOOL│      │    effective_start_ts   │      │       titles_cnt        │      │    etl_inserted_ts      │        │
│  │    month_end_flag  BOOL │      │    effective_end_ts     │      │    base_price_  NUMERIC │      │    etl_batch_id         │        │
│  │ ─── Service ─────────── │      │    is_current     BOOL  │      │       monthly           │      └───────────┬─────────────┘        │
│  │    etl_inserted_ts      │      │ ─── Service ─────────── │      │ ─── SCD2 ────────────── │                  │                      │
│  │    etl_batch_id         │      │    etl_inserted_ts      │      │    effective_start_ts   │                  │                      │
│  └───────────┬─────────────┘      │    etl_updated_ts       │      │    effective_end_ts     │                  │                      │
│              │                    │    etl_batch_id         │      │    is_current     BOOL  │                  │                      │
│              │                    │    hash_data_scd1       │      │ ─── Service ─────────── │                  │                      │
│              │                    │    hash_data_scd2       │      │    etl_inserted_ts      │                  │                      │
│              │                    └───────────┬─────────────┘      │    etl_updated_ts       │                  │                      │
│              │                                │                    │    etl_batch_id         │                  │                      │
│              │                                │                    │    hash_data_scd2       │                  │                      │
│              │                                │                    └───────────┬─────────────┘                  │                      │
│              │                                │                                │                                │                      │
│              │                                │                                │                                │                      │
│              │      ┌─────────────────────────┴────────────────────────────────┴────────────────────────────────┴──────┐               │
│              │      │                                                                                                  │               │
│              │      │                              ╔═══════════════════════════════════════════╗                       │               │
│              └──────┤                              ║      fact_subscription_event              ║                       │               │
│                     │                              ╠═══════════════════════════════════════════╣                       │               │
│                     │                              ║ PK subscription_event_id           STRING ║                       │               │
│  ┌──────────────────┤                              ║ DD subscription_id                 STRING ║                       ├───────────────┤
│  │                  │                              ║ DD contract_id                     STRING ║                       │               │
│  │                  │                              ║ ─────────────────────────────────────────  ║                       │               │
│  │                  │                              ║ FK event_date_key                   INT64 ║◄──────────────────────┤               │
│  │                  │                              ║ FK user_key                         INT64 ║                       │               │
│  │                  │                              ║ FK geo_key                          INT64 ║───────────────────────┼───────┐       │
│  │                  │                              ║ FK plan_key                         INT64 ║                       │       │       │
│  │                  │                              ║ FK term_key                         INT64 ║◄──────────────────────┘       │       │
│  │                  │                              ║ FK partner_store_key                INT64 ║───────────────────────────────┼───┐   │
│  │                  │                              ║ FK promotion_key                    INT64 ║───────────────────────────┐   │   │   │
│  │                  │                              ║ FK payment_method_key               INT64 ║───────────────────────┐   │   │   │   │
│  │                  │                              ║ FK currency_key                     INT64 ║───────────────────┐   │   │   │   │   │
│  │                  │                              ║ FK voucher_key                      INT64 ║───────────────┐   │   │   │   │   │   │
│  │                  │                              ║ FK status_key                       INT64 ║───────────┐   │   │   │   │   │   │   │
│  │                  │                              ║ ─────────────────────────────────────────  ║          │   │   │   │   │   │   │   │
│  │                  │                              ║    signup_count                     INT64 ║  Measure  │   │   │   │   │   │   │   │
│  │                  │                              ║    price_amount                   NUMERIC ║  Measure  │   │   │   │   │   │   │   │
│  │                  │                              ║    discount_amount                NUMERIC ║  Measure  │   │   │   │   │   │   │   │
│  │                  │                              ║    net_amount                     NUMERIC ║  Measure  │   │   │   │   │   │   │   │
│  │                  │                              ║    months_purchased                 INT64 ║  Measure  │   │   │   │   │   │   │   │
│  │                  │                              ║ ─────────────────────────────────────────  ║          │   │   │   │   │   │   │   │
│  │                  │                              ║    etl_inserted_ts               TIMESTAMP║  Service  │   │   │   │   │   │   │   │
│  │                  │                              ║    etl_batch_id                    STRING ║  Service  │   │   │   │   │   │   │   │
│  │                  │                              ╚═══════════════════════════════════════════╝           │   │   │   │   │   │   │   │
│  │                  │                                                                                      │   │   │   │   │   │   │   │
│  │                  └──────────────────────────────────────────────────────────────────────────────────────┼───┼───┼───┼───┼───┼───┼───┘
│  │                                                                                                         │   │   │   │   │   │   │
│  │  ┌─────────────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐          │   │   │   │   │   │   │
│  │  │     dim_status          │      │     dim_voucher         │      │     dim_currency        │          │   │   │   │   │   │   │
│  │  ├─────────────────────────┤      ├─────────────────────────┤      ├─────────────────────────┤          │   │   │   │   │   │   │
│  │  │ PK status_key     INT64 │      │ PK voucher_key    INT64 │      │ PK currency_key   INT64 │          │   │   │   │   │   │   │
│  │  │ BK status_code   STRING │      │ BK voucher_code  STRING │      │ BK iso_currency_ STRING │          │   │   │   │   │   │   │
│  │  │ ─────────────────────── │      │ ─────────────────────── │      │       code              │          │   │   │   │   │   │   │
│  │  │    status_name   STRING │      │    voucher_type  STRING │      │ ─────────────────────── │          │   │   │   │   │   │   │
│  │  │    status_group  STRING │      │    nominal_term   INT64 │      │    currency_name STRING │          │   │   │   │   │   │   │
│  │  │    is_active_     BOOL  │      │       _months           │      │    symbol        STRING │          │   │   │   │   │   │   │
│  │  │       status            │      │    nominal_value NUMERIC│      │    decimal_places INT64 │          │   │   │   │   │   │   │
│  └──┼───────────────┬─────────┘      │    expiry_date    DATE  │      └───────────┬─────────────┘          │   │   │   │   │   │   │
│     │               │                └───────────┬─────────────┘                  │                        │   │   │   │   │   │   │
│     │               │                            │                                │                        │   │   │   │   │   │   │
│     │               └────────────────────────────┼────────────────────────────────┼────────────────────────┘   │   │   │   │   │   │
│     │                                            │                                │                            │   │   │   │   │   │
│     │                                            └────────────────────────────────┼────────────────────────────┘   │   │   │   │   │
│     │                                                                             │                                │   │   │   │   │
│     │  ┌─────────────────────────┐      ┌─────────────────────────┐               │                                │   │   │   │   │
│     │  │   dim_payment_method    │      │     dim_promotion       │               │                                │   │   │   │   │
│     │  ├─────────────────────────┤      ├─────────────────────────┤               │                                │   │   │   │   │
│     │  │ PK payment_method_ INT64│      │ PK promotion_key  INT64 │               │                                │   │   │   │   │
│     │  │       key               │      │ BK promotion_code STRING│               │                                │   │   │   │   │
│     │  │ BK payment_method_      │      │ ─────────────────────── │               │                                │   │   │   │   │
│     │  │       code       STRING │      │    promotion_type STRING│               │                                │   │   │   │   │
│     │  │ ─────────────────────── │      │    promotion_name STRING│               │                                │   │   │   │   │
│     │  │    payment_type  STRING │      │    discount_pct NUMERIC │               └────────────────────────────────┘   │   │   │   │
│     │  │    provider      STRING │      │    start_date     DATE  │                                                    │   │   │   │
│     │  │    is_active      BOOL  │      │    end_date       DATE  │                                                    │   │   │   │
│     │  └───────────┬─────────────┘      └───────────┬─────────────┘                                                    │   │   │   │
│     │              │                                │                                                                  │   │   │   │
│     │              └────────────────────────────────┼──────────────────────────────────────────────────────────────────┘   │   │   │
│     │                                               │                                                                      │   │   │
│     │                                               └──────────────────────────────────────────────────────────────────────┘   │   │
│     │                                                                                                                          │   │
│     │  ┌─────────────────────────┐      ┌─────────────────────────┐                                                            │   │
│     │  │    dim_geography        │      │   dim_partner_store     │                                                            │   │
│     │  ├─────────────────────────┤      ├─────────────────────────┤                                                            │   │
│     │  │ PK geo_key        INT64 │      │ PK partner_store_ INT64 │                                                            │   │
│     │  │ BK geo_code      STRING │      │       key               │                                                            │   │
│     │  │ ─────────────────────── │      │ BK store_id      STRING │                                                            │   │
│     │  │    country_code  STRING │      │ ─────────────────────── │                                                            │   │
│     │  │    country       STRING │      │    store_name    STRING │                                                            │   │
│     │  │    region        STRING │      │    chain         STRING │                                                            │   │
│     │  │    city          STRING │      │    store_type    STRING │                                                            │   │
│     │  │    latitude_bucket      │      │    geo_key        INT64 │                                                            │   │
│     │  │                  STRING │      │    is_active       BOOL │                                                            │   │
│     │  │    timezone      STRING │      └───────────┬─────────────┘                                                            │   │
│     │  └───────────┬─────────────┘                  │                                                                          │   │
│     │              │                                │                                                                          │   │
│     │              └────────────────────────────────┴──────────────────────────────────────────────────────────────────────────┘   │
│     │                                                                                                                              │
└─────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Example 2: fact_viewing_session (Detailed) — Fraud Detection Star

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                                          │
│  ┌────────────────────────┐     ┌────────────────────────┐     ┌────────────────────────┐     ┌────────────────────────┐ │
│  │      dim_date          │     │      dim_time          │     │      dim_user          │     │      dim_profile       │ │
│  ├────────────────────────┤     ├────────────────────────┤     ├────────────────────────┤     ├────────────────────────┤ │
│  │ PK date_key      INT64 │     │ PK time_key      INT64 │     │ PK user_key      INT64 │     │ PK profile_key   INT64 │ │
│  │ BK calendar_date  DATE │     │ BK hhmmss       STRING │     │ BK user_id      STRING │     │ BK profile_id   STRING │ │
│  │ ────────────────────── │     │ ────────────────────── │     │ ────────────────────── │     │ ────────────────────── │ │
│  │    year          INT64 │     │    hour          INT64 │     │    email_hash   STRING │     │    profile_name STRING │ │
│  │    month         INT64 │     │    minute        INT64 │     │    signup_date   INT64 │     │    age_band     STRING │ │
│  │    day           INT64 │     │    day_part     STRING │     │    account_status      │     │    gender       STRING │ │
│  │    day_of_week   INT64 │     │    is_prime_time BOOL  │     │                 STRING │     │    habitual_city       │ │
│  │    is_weekend     BOOL │     └──────────┬─────────────┘     │ ─── SCD2 ─────────────│     │                 STRING │ │
│  └──────────┬─────────────┘                │                   │    effective_start_ts │     │    is_family_   BOOL   │ │
│             │                              │                   │    is_current    BOOL │     │       default          │ │
│             │                              │                   └──────────┬─────────────┘     │ ─── SCD2 ──────────── │ │
│             │                              │                              │                   │    effective_start_ts │ │
│             │                              │                              │                   │    is_current    BOOL │ │
│             │                              │                              │                   └──────────┬─────────────┘ │
│             │      ┌───────────────────────┴──────────────────────────────┴──────────────────────────────┘              │
│             │      │                                                                                                    │
│             │      │                       ╔════════════════════════════════════════════════╗                           │
│             └──────┤                       ║        fact_viewing_session                    ║                           │
│                    │                       ╠════════════════════════════════════════════════╣                           │
│                    │                       ║ PK session_id                          STRING  ║  DD                       │
│                    │                       ║ ────────────────────────────────────────────── ║                           │
│                    │                       ║    start_ts                          TIMESTAMP ║  ← For fraud detection   │
│                    │                       ║    end_ts                            TIMESTAMP ║  ← Session overlap check │
│                    │                       ║ ────────────────────────────────────────────── ║                           │
│                    │                       ║ FK start_date_key                       INT64  ║◄────────────────────────┐ │
│                    │                       ║ FK start_time_key                       INT64  ║                         │ │
│                    │                       ║ FK user_key                             INT64  ║                         │ │
│                    │                       ║ FK profile_key                          INT64  ║  ← Fraud: multi-profile │ │
│                    │                       ║ FK geo_key                              INT64  ║  ← Fraud: multi-geo     │ │
│  ┌─────────────────┤                       ║ FK plan_key                             INT64  ║                         │ │
│  │                 │                       ║ FK device_key                           INT64  ║                         │ │
│  │                 │                       ║ FK content_key                          INT64  ║─────────────────────┐   │ │
│  │                 │                       ║ FK status_key                           INT64  ║                     │   │ │
│  │                 │                       ║ ────────────────────────────────────────────── ║                     │   │ │
│  │                 │                       ║    watch_seconds                         INT64 ║  Measure (additive) │   │ │
│  │                 │                       ║    session_count                         INT64 ║  Measure (=1)       │   │ │
│  │                 │                       ║    concurrent_stream_flag                 BOOL ║  ← Fraud flag       │   │ │
│  │                 │                       ║ ────────────────────────────────────────────── ║                     │   │ │
│  │                 │                       ║    etl_inserted_ts                   TIMESTAMP ║  Service            │   │ │
│  │                 │                       ║    etl_batch_id                        STRING  ║  Service            │   │ │
│  │                 │                       ╚════════════════════════════════════════════════╝                     │   │ │
│  │                 │                                                                                              │   │ │
│  │                 └──────────────────────────────────────────────────────────────────────────────────────────────┼───┘ │
│  │                                                                                                                │     │
│  │  ┌────────────────────────┐     ┌────────────────────────┐     ┌────────────────────────┐                      │     │
│  │  │     dim_geography      │     │      dim_device        │     │      dim_content       │                      │     │
│  │  ├────────────────────────┤     ├────────────────────────┤     ├────────────────────────┤                      │     │
│  │  │ PK geo_key       INT64 │     │ PK device_key    INT64 │     │ PK content_key   INT64 │                      │     │
│  │  │ BK geo_code     STRING │     │ BK device_id    STRING │     │ BK content_id   STRING │                      │     │
│  │  │ ────────────────────── │     │ ────────────────────── │     │ ────────────────────── │                      │     │
│  │  │    country      STRING │     │    device_type  STRING │     │    title        STRING │                      │     │
│  │  │    region       STRING │     │    manufacturer STRING │     │    content_type STRING │                      │     │
│  │  │    city         STRING │     │    os           STRING │     │    genre        STRING │                      │     │
│  │  │    latitude_bucket     │     │    os_version   STRING │     │    release_year  INT64 │                      │     │
│  │  │                 STRING │     │    app_version  STRING │     │    duration_minutes    │                      │     │
│  │  │    longitude_bucket    │     │    screen_resolution   │     │                  INT64 │                      │     │
│  │  │                 STRING │     │                 STRING │     │    maturity_rating     │                      │     │
│  │  │ ← For fraud: geo check │     └──────────┬─────────────┘     │                 STRING │                      │     │
│  └──┼────────────────────────┘                │                   └──────────┬─────────────┘                      │     │
│     │                                         │                              │                                    │     │
│     └─────────────────────────────────────────┴──────────────────────────────┴────────────────────────────────────┘     │
│                                                                                                                          │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Key fraud detection fields:**
- `start_ts` + `end_ts` → detect overlapping sessions
- `geo_key` (with `latitude_bucket`, `longitude_bucket`) → detect multiple locations
- `profile_key` → track which profile is streaming
- `concurrent_stream_flag` → pre-calculated fraud indicator

---

## Table of Contents

1. [Star_Subscription_Event](#1-star_subscription_event)
2. [Star_Subscription_Snapshot](#2-star_subscription_snapshot)
3. [Star_Plan_Change](#3-star_plan_change)
4. [Star_Voucher_Sale](#4-star_voucher_sale)
5. [Star_Voucher_Lifecycle](#5-star_voucher_lifecycle)
6. [Star_Viewing_Session](#6-star_viewing_session)
7. [Star_Content_Tx](#7-star_content_tx)
8. [Star_Referral_Edge](#8-star_referral_edge)
9. [Star_Referral_Bonus](#9-star_referral_bonus)
10. [Star_Device_Link](#10-star_device_link)
11. [Star_Profile_Event](#11-star_profile_event)
12. [Star_Region_Demographics](#12-star_region_demographics)

---

## 1. Star_Subscription_Event

**Grain:** 1 row per subscription purchase/activation (incl. renewals, voucher conversions, TV bundle)

**Measures:** `signup_count`, `price_amount`, `discount_amount`, `months_purchased`

```
                              ┌──────────────────┐
                              │     dim_date     │
                              │  (event_date)    │
                              └────────┬─────────┘
                                       │
       ┌──────────────────┐            │            ┌──────────────────┐
       │    dim_status    │────────────┤            │    dim_term      │
       │ (subscription    │            │            │   (1/3/12/24)    │
       │     status)      │            │            └────────┬─────────┘
       └──────────────────┘            │                     │
                                       │                     │
       ┌──────────────────┐            ▼                     │
       │   dim_voucher    │     ┌─────────────────────┐      │
       │   (optional)     │─────│                     │◄─────┘
       └──────────────────┘     │ fact_subscription_  │
                                │       event         │      ┌──────────────────┐
       ┌──────────────────┐     │                     │──────│    dim_plan      │
       │  dim_currency    │─────│  • signup_count     │      └──────────────────┘
       └──────────────────┘     │  • price_amount     │
                                │  • discount_amount  │      ┌──────────────────┐
       ┌──────────────────┐     │  • months_purchased │──────│    dim_user      │
       │ dim_payment_     │─────│                     │      └──────────────────┘
       │    method        │     └─────────┬───────────┘
       └──────────────────┘               │                  ┌──────────────────┐
                                          │                  │  dim_geography   │
       ┌──────────────────┐               │                  └────────┬─────────┘
       │  dim_promotion   │───────────────┤                           │
       │ (VOUCHER/BUNDLE/ │               │                           │
       │    REFERRAL)     │               │           ┌───────────────┘
       └──────────────────┘               │           │
                                          │           │
                              ┌───────────┴───────────┴──────┐
                              │      dim_partner_store       │
                              │    (TV retailers, optional)  │
                              └──────────────────────────────┘
```

---

## 2. Star_Subscription_Snapshot

**Grain:** 1 row per user per month per subscription (as-of month start)

**Measures:** `active_flag`, `active_subscriptions`, `mrr_amount`, `tenure_months`

```
                              ┌──────────────────┐
                              │     dim_date     │
                              │ (month_start)    │
                              └────────┬─────────┘
                                       │
                                       │
       ┌──────────────────┐            │            ┌──────────────────┐
       │    dim_status    │────────────┤            │    dim_term      │
       │ (active/canceled)│            │            │   (1/3/12/24)    │
       └──────────────────┘            │            └────────┬─────────┘
                                       │                     │
                                       │                     │
                                       ▼                     │
                                ┌─────────────────────┐      │
                                │                     │◄─────┘
                                │ fact_subscription_  │
                                │  monthly_snapshot   │      ┌──────────────────┐
                                │                     │──────│    dim_plan      │
                                │ • active_flag       │      └──────────────────┘
                                │ • active_subs       │
                                │ • mrr_amount        │      ┌──────────────────┐
                                │ • tenure_months     │──────│    dim_user      │
                                │                     │      └──────────────────┘
                                └─────────┬───────────┘
                                          │
                                          │
                                          │
                              ┌───────────┴───────────┐
                              │     dim_geography     │
                              └───────────────────────┘
```

---

## 3. Star_Plan_Change

**Grain:** 1 row per plan change (upgrade/downgrade/cancel/non-renew)

**Measures:** `change_count`, `delta_mrr`, `churn_flag`

```
                              ┌──────────────────┐
                              │     dim_date     │
                              │  (change_date)   │
                              └────────┬─────────┘
                                       │
                                       │
       ┌──────────────────┐            │            ┌──────────────────┐
       │    dim_status    │────────────┤            │   dim_device     │
       │  (change reason) │            │            │   (optional)     │
       └──────────────────┘            │            └────────┬─────────┘
                                       │                     │
                                       │                     │
                                       ▼                     │
                                ┌─────────────────────┐      │
                                │                     │◄─────┘
                                │  fact_plan_change   │
                                │                     │      ┌──────────────────┐
       ┌──────────────────┐     │  • change_count     │──────│    dim_user      │
       │   dim_promotion  │─────│  • delta_mrr        │      └──────────────────┘
       │    (optional)    │     │  • churn_flag       │
       └──────────────────┘     │                     │      ┌──────────────────┐
                                └─────────┬───────────┘──────│  dim_geography   │
                                          │                  └──────────────────┘
                                          │
                          ┌───────────────┴───────────────┐
                          │                               │
                 ┌────────┴────────┐             ┌────────┴────────┐
                 │    dim_plan     │             │    dim_plan     │
                 │  (from_plan)    │             │   (to_plan)     │
                 │  ═══════════════│             │  ═══════════════│
                 │  ROLE-PLAYING   │             │  ROLE-PLAYING   │
                 └─────────────────┘             └─────────────────┘
```

---

## 4. Star_Voucher_Sale

**Grain:** 1 row per voucher sold at distribution point

**Measures:** `voucher_sale_count`, `voucher_price_amount` (1 UAH)

```
                              ┌──────────────────┐
                              │     dim_date     │
                              │   (sale_date)    │
                              └────────┬─────────┘
                                       │
                                       │
       ┌──────────────────┐            │            ┌──────────────────┐
       │   dim_prospect   │────────────┤            │  dim_promotion   │
       │ (lead at sale)   │            │            │(voucher campaign)│
       └──────────────────┘            │            └────────┬─────────┘
                                       │                     │
                                       │                     │
                                       ▼                     │
                                ┌─────────────────────┐      │
                                │                     │◄─────┘
                                │  fact_voucher_sale  │
                                │                     │      ┌──────────────────┐
                                │ • voucher_sale_     │──────│  dim_geography   │
                                │      count          │      │ (city at sale)   │
                                │ • voucher_price_    │      └──────────────────┘
                                │      amount         │
                                │                     │      ┌──────────────────┐
                                └─────────┬───────────┘──────│   dim_voucher    │
                                          │                  └──────────────────┘
                                          │
                              ┌───────────┴───────────┐
                              │   dim_partner_store   │
                              │  (distribution point) │
                              └───────────────────────┘
```

---

## 5. Star_Voucher_Lifecycle

**Grain:** 1 row per voucher, updated at milestones (sale → activation → conversion)

**Measures:** `lag_sale_to_activation_days`, `lag_activation_to_conversion_days`, `is_activated_flag`, `is_converted_flag`

**Type:** Accumulating Snapshot

```
                    ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
                    │     dim_date     │   │     dim_date     │   │     dim_date     │
                    │   (sale_date)    │   │ (activation_date)│   │(conversion_date) │
                    │  ════════════════│   │  ════════════════│   │  ════════════════│
                    │  ROLE-PLAYING    │   │  ROLE-PLAYING    │   │  ROLE-PLAYING    │
                    └────────┬─────────┘   └────────┬─────────┘   └────────┬─────────┘
                             │                      │                      │
                             └──────────────────────┼──────────────────────┘
                                                    │
       ┌──────────────────┐                         │                  ┌──────────────────┐
       │   dim_prospect   │─────────────────────────┤                  │    dim_status    │
       └──────────────────┘                         │                  │ (Issued/Activated│
                                                    │                  │ /Converted/Exprd)│
                                                    ▼                  └────────┬─────────┘
                                             ┌─────────────────────┐            │
       ┌──────────────────┐                  │                     │◄───────────┘
       │  dim_geography   │──────────────────│ fact_voucher_       │
       └──────────────────┘                  │     lifecycle       │      ┌──────────────────┐
                                             │                     │──────│   dim_voucher    │
       ┌──────────────────┐                  │ • lag_sale_to_      │      └──────────────────┘
       │ dim_partner_store│──────────────────│      activation     │
       └──────────────────┘                  │ • lag_activation_   │      ┌──────────────────┐
                                             │      to_conversion  │──────│  dim_promotion   │
                                             │ • is_activated_flag │      └──────────────────┘
                                             │ • is_converted_flag │
                                             └─────────────────────┘
```

---

## 6. Star_Viewing_Session

**Grain:** 1 row per playback session (user-profile-content)

**Measures:** `watch_seconds`, `session_count`

```
                    ┌──────────────────┐             ┌──────────────────┐
                    │     dim_date     │             │     dim_time     │
                    │  (start_date)    │             │  (start_time)    │
                    └────────┬─────────┘             └────────┬─────────┘
                             │                                │
                             └────────────────┬───────────────┘
                                              │
       ┌──────────────────┐                   │                  ┌──────────────────┐
       │    dim_status    │───────────────────┤                  │   dim_content    │
       │(playback status) │                   │                  │(movie/show/TV)   │
       └──────────────────┘                   │                  └────────┬─────────┘
                                              │                           │
                                              ▼                           │
                                       ┌─────────────────────┐            │
       ┌──────────────────┐            │                     │◄───────────┘
       │   dim_device     │────────────│ fact_viewing_       │
       └──────────────────┘            │      session        │      ┌──────────────────┐
                                       │                     │──────│    dim_user      │
       ┌──────────────────┐            │  • watch_seconds    │      └──────────────────┘
       │    dim_plan      │────────────│  • session_count    │
       │   (optional)     │            │                     │      ┌──────────────────┐
       └──────────────────┘            └─────────┬───────────┘──────│   dim_profile    │
                                                 │                  │ (age/gender/etc) │
                                                 │                  └──────────────────┘
                                     ┌───────────┴───────────┐
                                     │     dim_geography     │
                                     │    (geo at session)   │
                                     └───────────────────────┘
```

---

## 7. Star_Content_Tx

**Grain:** 1 row per content purchase or rental transaction

**Measures:** `tx_count`, `gross_amount`, `net_amount`, `royalty_amount`

```
                    ┌──────────────────┐             ┌──────────────────┐
                    │     dim_date     │             │     dim_time     │
                    │   (tx_date)      │             │   (tx_time)      │
                    └────────┬─────────┘             └────────┬─────────┘
                             │                                │
                             └────────────────┬───────────────┘
                                              │
       ┌──────────────────┐                   │                  ┌──────────────────┐
       │    dim_status    │───────────────────┤                  │   dim_content    │
       │(purchase/rental) │                   │                  └────────┬─────────┘
       └──────────────────┘                   │                           │
                                              ▼                           │
       ┌──────────────────┐            ┌─────────────────────┐            │
       │  dim_currency    │────────────│                     │◄───────────┘
       └──────────────────┘            │  fact_content_tx    │
                                       │                     │      ┌──────────────────┐
       ┌──────────────────┐            │  • tx_count         │──────│ dim_rights_holder│
       │ dim_payment_     │────────────│  • gross_amount     │      └──────────────────┘
       │    method        │            │  • net_amount       │
       └──────────────────┘            │  • royalty_amount   │      ┌──────────────────┐
                                       │                     │──────│    dim_user      │
       ┌──────────────────┐            └─────────┬───────────┘      └──────────────────┘
       │  dim_promotion   │──────────────────────┤
       │   (optional)     │                      │                  ┌──────────────────┐
       └──────────────────┘            ┌─────────┴───────┐          │   dim_profile    │
                                       │                 │          └────────┬─────────┘
                           ┌───────────┴──────┐   ┌──────┴──────────┐        │
                           │  dim_geography   │   │   dim_device    │◄───────┘
                           └──────────────────┘   └─────────────────┘
```

---

## 8. Star_Referral_Edge

**Grain:** 1 row per direct referral (referrer → friend)

**Measures:** `referral_count` (factless = 1)

```
                              ┌──────────────────┐
                              │     dim_date     │
                              │ (referral_date)  │
                              └────────┬─────────┘
                                       │
                                       │
                                       │
                                       │
                                       ▼
                                ┌─────────────────────┐
                                │                     │
       ┌──────────────────┐     │ fact_referral_edge  │     ┌──────────────────┐
       │  dim_promotion   │─────│                     │─────│    dim_user      │
       │ (REFERRAL        │     │ • referral_count    │     │   (referrer)     │
       │   campaign)      │     │      = 1            │     │  ════════════════│
       └──────────────────┘     │                     │     │  ROLE-PLAYING    │
                                └─────────┬───────────┘     └──────────────────┘
                                          │
                                          │
                                          │
                                ┌─────────┴───────────┐
                                │      dim_user       │
                                │     (referred)      │
                                │  ═══════════════════│
                                │    ROLE-PLAYING     │
                                └─────────────────────┘
```

---

## 9. Star_Referral_Bonus

**Grain:** 1 row per bonus payout event (direct=50, indirect=5 by depth≥2)

**Measures:** `bonus_amount`, `bonus_count`

```
                              ┌──────────────────┐
                              │     dim_date     │
                              │  (bonus_date)    │
                              └────────┬─────────┘
                                       │
                                       │
       ┌──────────────────┐            │            ┌──────────────────┐
       │ dim_referral_    │────────────┤            │  dim_currency    │
       │     depth        │            │            └────────┬─────────┘
       │ (1=direct,       │            │                     │
       │  ≥2=indirect)    │            │                     │
       └──────────────────┘            ▼                     │
                                ┌─────────────────────┐      │
                                │                     │◄─────┘
       ┌──────────────────┐     │ fact_referral_      │
       │  dim_promotion   │─────│     bonus_tx        │     ┌──────────────────┐
       │ (REFERRAL        │     │                     │─────│    dim_user      │
       │   campaign)      │     │ • bonus_amount      │     │  (beneficiary)   │
       └──────────────────┘     │ • bonus_count       │     │  ════════════════│
                                │                     │     │  ROLE-PLAYING    │
                                └─────────┬───────────┘     └──────────────────┘
                                          │
                                          │
                                ┌─────────┴───────────┐
                                │      dim_user       │
                                │   (originating)     │
                                │  ═══════════════════│
                                │    ROLE-PLAYING     │
                                └─────────────────────┘
```

---

## 10. Star_Device_Link

**Grain:** 1 row per user-device link/unlink event

**Measures:** `link_count` (factless = 1)

```
                              ┌──────────────────┐
                              │     dim_date     │
                              │  (event_date)    │
                              └────────┬─────────┘
                                       │
                                       │
                                       │
                                       │
                                       ▼
                                ┌─────────────────────┐
                                │                     │
       ┌──────────────────┐     │  fact_device_link   │     ┌──────────────────┐
       │    dim_status    │─────│                     │─────│    dim_user      │
       │ (LINKED/UNLINKED)│     │ • link_count = 1    │     └──────────────────┘
       └──────────────────┘     │                     │
                                └─────────┬───────────┘
                                          │
                                          │
                                ┌─────────┴───────────┐
                                │     dim_device      │
                                └─────────────────────┘
```

---

## 11. Star_Profile_Event

**Grain:** 1 row per profile create/update event

**Measures:** `profile_event_count` (factless = 1)

```
                              ┌──────────────────┐
                              │     dim_date     │
                              │  (event_date)    │
                              └────────┬─────────┘
                                       │
                                       │
       ┌──────────────────┐            │            ┌──────────────────┐
       │    dim_status    │────────────┤            │   dim_profile    │
       │(CREATED/UPDATED) │            │            └────────┬─────────┘
       └──────────────────┘            │                     │
                                       │                     │
                                       ▼                     │
                                ┌─────────────────────┐      │
                                │                     │◄─────┘
                                │ fact_profile_event  │
                                │                     │      ┌──────────────────┐
                                │ • profile_event_    │──────│    dim_user      │
                                │      count = 1      │      └──────────────────┘
                                │                     │
                                └─────────┬───────────┘
                                          │
                                          │
                              ┌───────────┴───────────┐
                              │     dim_geography     │
                              └───────────────────────┘
```

---

## 12. Star_Region_Demographics

**Grain:** 1 row per region per year (or month)

**Measures:** `population`, `target_demo_population`, `penetration_rate` (derived)

```
                              ┌──────────────────┐
                              │     dim_date     │
                              │  (year_date)     │
                              └────────┬─────────┘
                                       │
                                       │
                                       │
                                       │
                                       ▼
                                ┌─────────────────────┐
                                │                     │
       ┌──────────────────┐     │ fact_region_        │     ┌──────────────────┐
       │    dim_status    │─────│    demographics     │─────│  dim_geography   │
       │ (source/version) │     │                     │     │  (region-level)  │
       └──────────────────┘     │ • population        │     └──────────────────┘
                                │ • target_demo_      │
                                │      population     │
                                │ • penetration_rate  │
                                │      (derived)      │
                                └─────────────────────┘
```

---

## Legend

| Symbol | Meaning |
|--------|---------|
| `┌─────┐` | Dimension table |
| `┌═════┐` / `════` | Role-playing dimension (same table, different FK) |
| `──────►` | Foreign key relationship |
| `•` | Measure in fact table |
| `PK` | Primary Key |
| `FK` | Foreign Key |
| `DD` | Degenerate Dimension |

---

## Bus Matrix Summary

| Fact Table                       | Date | Time | User | Profile | Prospect | Geo | Plan | Term | Device | Content | Rights Holder | Partner Store | Voucher | Promotion | Payment Method | Currency | Referral Depth | Status |
|:---------------------------------|:----:|:----:|:----:|:-------:|:--------:|:---:|:----:|:----:|:------:|:-------:|:-------------:|:-------------:|:-------:|:---------:|:--------------:|:--------:|:--------------:|:------:|
| subscription_event               | ✗    |      | ✗    |         |          | ✗   | ✗    | ✗    |        |         |               | ✗             | ✗       | ✗         | ✗              | ✗        |                | ✗      |
| subscription_monthly_snapshot    | ✗    |      | ✗    |         |          | ✗   | ✗    | ✗    |        |         |               |               |         |           |                |          |                | ✗      |
| plan_change                      | ✗    |      | ✗    |         |          | ✗   | ✗    |      | ✗      |         |               |               |         | ✗         |                |          |                | ✗      |
| voucher_sale                     | ✗    |      |      |         | ✗        | ✗   |      |      |        |         |               | ✗             | ✗       | ✗         |                |          |                |        |
| voucher_lifecycle                | ✗    |      |      |         | ✗        | ✗   |      |      |        |         |               | ✗             | ✗       | ✗         |                |          |                | ✗      |
| viewing_session                  | ✗    | ✗    | ✗    | ✗       |          | ✗   | ✗    |      | ✗      | ✗       |               |               |         |           |                |          |                | ✗      |
| content_tx                       | ✗    | ✗    | ✗    | ✗       |          | ✗   |      |      | ✗      | ✗       | ✗             |               |         | ✗         | ✗              | ✗        |                | ✗      |
| referral_edge                    | ✗    |      | ✗    |         |          |     |      |      |        |         |               |               |         | ✗         |                |          |                |        |
| referral_bonus_tx                | ✗    |      | ✗    |         |          |     |      |      |        |         |               |               |         | ✗         |                | ✗        | ✗              |        |
| device_link                      | ✗    |      | ✗    |         |          |     |      |      | ✗      |         |               |               |         |           |                |          |                | ✗      |
| profile_event                    | ✗    |      | ✗    | ✗       |          | ✗   |      |      |        |         |               |               |         |           |                |          |                | ✗      |
| region_demographics              | ✗    |      |      |         |          | ✗   |      |      |        |         |               |               |         |           |                |          |                | ✗      |

---

_Generated from Netflix_BusMatrix_Logical_Data_Model_BQ.md_

