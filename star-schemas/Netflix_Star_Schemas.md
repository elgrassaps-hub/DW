# Netflix Data Warehouse - Star Schemas

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

**Measures:** `population`, `target_demo_population`, `market_coverage_pct` (derived)

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
                                │ • market_coverage_  │
                                │      (derived)      │
                                └─────────────────────┘
```

---

## Bus Matrix Summary


| Fact Table                    | Date | User | Geo | Status | Promotion | Plan | Device | Profile | Partner Store | Voucher | Currency | Term | Time | Content | Prospect | Payment Method | Rights Holder | Referral Depth |
|:------------------------------|:----:|:----:|:---:|:------:|:---------:|:----:|:------:|:-------:|:-------------:|:-------:|:--------:|:----:|:----:|:-------:|:--------:|:--------------:|:-------------:|:--------------:|
| subscription_event            | ✗    | ✗    | ✗   | ✗      | ✗         | ✗    |        |         | ✗             | ✗       | ✗        | ✗    |      |         |          | ✗              |               |                |
| subscription_monthly_snapshot | ✗    | ✗    | ✗   | ✗      |           | ✗    |        |         |               |         |          | ✗    |      |         |          |                |               |                |
| plan_change                   | ✗    | ✗    | ✗   | ✗      | ✗         | ✗    | ✗      |         |               |         |          |      |      |         |          |                |               |                |
| voucher_sale                  | ✗    |      | ✗   |        | ✗         |      |        |         | ✗             | ✗       |          |      |      |         | ✗        |                |               |                |
| voucher_lifecycle             | ✗    |      | ✗   | ✗      | ✗         |      |        |         | ✗             | ✗       |          |      |      |         | ✗        |                |               |                |
| viewing_session               | ✗    | ✗    | ✗   | ✗      |           | ✗    | ✗      | ✗       |               |         |          |      | ✗    | ✗       |          |                |               |                |
| content_tx                    | ✗    | ✗    | ✗   | ✗      | ✗         |      | ✗      | ✗       |               |         | ✗        |      | ✗    | ✗       |          | ✗              | ✗             |                |
| referral_edge                 | ✗    | ✗    |     |        | ✗         |      |        |         |               |         |          |      |      |         |          |                |               |                |
| referral_bonus_tx             | ✗    | ✗    |     |        | ✗         |      |        |         |               |         | ✗        |      |      |         |          |                |               | ✗              |
| device_link                   | ✗    | ✗    |     | ✗      |           |      | ✗      |         |               |         |          |      |      |         |          |                |               |                |
| profile_event                 | ✗    | ✗    | ✗   | ✗      |           |      |        | ✗       |               |         |          |      |      |         |          |                |               |                |
| region_demographics           | ✗    |      | ✗   | ✗      |           |      |        |         |               |         |          |      |      |         |          |                |               |                |

---

## Grain & Metrics by Fact Table

| Fact Table                    | Grain (Гранулярність)                                      | Key Metrics (Метрики)                                                    |
|:------------------------------|:-----------------------------------------------------------|:-------------------------------------------------------------------------|
| subscription_event            | 1 row per subscription purchase/activation event           | signup_count, price_amount, discount_amount, net_amount, months_purchased |
| subscription_monthly_snapshot | 1 row per user per month per subscription (month start)    | active_subscriptions, active_flag, mrr_amount, tenure_months             |
| plan_change                   | 1 row per plan change (upgrade/downgrade/cancel)           | change_count, delta_mrr, churn_flag                                      |
| voucher_sale                  | 1 row per voucher sold at distribution point               | voucher_sale_count, voucher_price_amount (1 UAH)                         |
| voucher_lifecycle             | 1 row per voucher (accumulating snapshot)                  | lag_sale_to_activation_days, lag_activation_to_conversion_days, is_activated_flag, is_converted_flag |
| viewing_session               | 1 row per playback session (user-profile-content)          | watch_seconds, session_count, concurrent_stream_flag                     |
| content_tx                    | 1 row per content purchase or rental transaction           | tx_count, gross_amount, net_amount, royalty_amount                       |
| referral_edge                 | 1 row per direct referral (referrer → friend)              | referral_count (factless = 1)                                            |
| referral_bonus_tx             | 1 row per bonus payout event (50 UAH direct, 5 UAH indirect)| bonus_count, bonus_amount                                                |
| device_link                   | 1 row per user-device link/unlink event                    | link_count (factless = 1)                                                |
| profile_event                 | 1 row per profile create/update event                      | profile_event_count (factless = 1)                                       |
| region_demographics           | 1 row per region per year (public demographic data)        | population, target_demo_population, households_count, internet_penetration_pct |
