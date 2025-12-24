-- ============================================
-- NETFLIX DATA WAREHOUSE - BigQuery DDL
-- ============================================
--
-- SETUP INSTRUCTIONS
--
-- Prerequisites:
--   1. GCP project with billing enabled
--   2. BigQuery API enabled (APIs & Services > Enable APIs)
--   3. Permissions: BigQuery Data Editor or BigQuery Admin
--
-- ============================================
-- OPTION A: Google Cloud Console (UI)
-- ============================================
--   1. Go to console.cloud.google.com
--   2. Select your project from the dropdown
--   3. Navigate: Menu > BigQuery
--   4. Create dataset:
--      - Click "+ CREATE DATASET" in Explorer panel
--      - Dataset ID: netflix_dw
--      - Data location: EU (or your preferred region)
--      - Default table expiration: Leave empty
--      - Click "CREATE DATASET"
--   5. Run DDL:
--      - Click "COMPOSE NEW QUERY" (or + icon)
--      - Copy this entire script
--      - Replace YOUR_PROJECT.YOUR_DATASET with: your-project-id.netflix_dw
--      - Click "RUN"
--   6. Verify: Expand netflix_dw dataset to see all tables
--
-- ============================================
-- OPTION B: gcloud CLI / bq command-line
-- ============================================
--   # Install gcloud SDK if not already: https://cloud.google.com/sdk/docs/install
--
--   # Authenticate
--   gcloud auth login
--   gcloud config set project YOUR_PROJECT_ID
--
--   # Create dataset
--   bq mk --location=EU --dataset YOUR_PROJECT_ID:netflix_dw
--
--   # Run DDL (after replacing YOUR_PROJECT.YOUR_DATASET in this file)
--   bq query --use_legacy_sql=false --project_id=YOUR_PROJECT_ID < Netflix_BigQuery_DDL.sql
--
--   # Or run inline (for quick test):
--   bq query --use_legacy_sql=false "CREATE TABLE IF NOT EXISTS netflix_dw.dim_date (...)"
--
--   # Verify tables created
--   bq ls netflix_dw
--
-- ============================================
-- OPTION C: Terraform (Infrastructure as Code)
-- ============================================
--   # See: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_table
--   # Example in separate .tf file
--
-- ============================================
--
-- TODO: replace YOUR_PROJECT.YOUR_DATASET with your-project-id.netflix_dw

-- Dimensions

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.dim_date` (
  date_key INT64 NOT NULL,            -- yyyymmdd
  calendar_date DATE NOT NULL,
  year INT64,
  quarter INT64,
  month INT64,
  day INT64,
  day_of_week INT64,
  month_start_flag BOOL,
  month_end_flag BOOL
);

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.dim_time` (
  time_key INT64 NOT NULL,            -- hhmmss as int (e.g., 235959)
  hhmmss STRING,
  hour INT64,
  minute INT64,
  second INT64,
  day_part STRING                    -- e.g., morning/afternoon/evening/night
);

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.dim_geography` (
  geo_key INT64 NOT NULL,
  country_code STRING,
  country STRING,
  region STRING,
  city STRING,
  latitude_bucket STRING,
  longitude_bucket STRING
);

-- user dim (SCD2)
CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.dim_user` (
  user_key INT64 NOT NULL,
  user_id STRING NOT NULL,            -- business key
  effective_start_ts TIMESTAMP NOT NULL,
  effective_end_ts TIMESTAMP,
  is_current BOOL NOT NULL,
  signup_date_key INT64,
  current_geo_key INT64,
  signup_channel STRING,
  email_hash STRING
);

-- profile dim
CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.dim_profile` (
  profile_key INT64 NOT NULL,
  profile_id STRING NOT NULL,         -- business key
  user_id STRING NOT NULL,
  effective_start_ts TIMESTAMP NOT NULL,
  effective_end_ts TIMESTAMP,
  is_current BOOL NOT NULL,
  age_band STRING,
  gender STRING,
  habitual_city STRING,
  is_family_default BOOL
);

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.dim_plan` (
  plan_key INT64 NOT NULL,
  plan_code STRING NOT NULL,          -- business key
  effective_start_ts TIMESTAMP NOT NULL,
  effective_end_ts TIMESTAMP,
  is_current BOOL NOT NULL,
  plan_name STRING,
  included_channels_cnt INT64,
  included_titles_cnt INT64
);

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.dim_term` (
  term_key INT64 NOT NULL,
  term_months INT64 NOT NULL          -- 1, 3, 12, 24
);

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.dim_device` (
  device_key INT64 NOT NULL,
  device_id STRING NOT NULL,
  device_type STRING,
  os STRING,
  app_version STRING
);

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.dim_content` (
  content_key INT64 NOT NULL,
  content_id STRING NOT NULL,
  title STRING,
  content_type STRING,                -- movie/show/channel/...
  genre STRING,
  release_year INT64
);

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.dim_rights_holder` (
  rights_holder_key INT64 NOT NULL,
  rights_holder_id STRING NOT NULL,
  name STRING,
  contract_type STRING
);

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.dim_partner_store` (
  partner_store_key INT64 NOT NULL,
  store_id STRING NOT NULL,
  store_name STRING,
  chain STRING,
  geo_key INT64
);

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.dim_promotion` (
  promotion_key INT64 NOT NULL,
  promotion_code STRING NOT NULL,
  promotion_type STRING,              -- VOUCHER / TV_BUNDLE / REFERRAL / NONE
  description STRING
);

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.dim_payment_method` (
  payment_method_key INT64 NOT NULL,
  payment_method_code STRING NOT NULL,
  provider STRING
);

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.dim_currency` (
  currency_key INT64 NOT NULL,
  iso_currency_code STRING NOT NULL,
  currency_name STRING
);

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.dim_voucher` (
  voucher_key INT64 NOT NULL,
  voucher_code STRING NOT NULL,
  voucher_type STRING,
  nominal_term_months INT64
);

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.dim_referral_depth` (
  depth_key INT64 NOT NULL,
  depth INT64 NOT NULL                 -- 1=direct, 2+=indirect
);

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.dim_status` (
  status_key INT64 NOT NULL,
  status_code STRING NOT NULL,         -- subscription/voucher/playback statuses
  status_group STRING
);

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.dim_prospect` (
  prospect_key INT64 NOT NULL,
  lead_id STRING,
  phone_hash STRING,
  effective_start_ts TIMESTAMP,
  effective_end_ts TIMESTAMP,
  is_current BOOL,
  age_band STRING,
  gender STRING,
  city_at_sale STRING,
  geo_key INT64
);

-- Facts
-- TODO: verify partition/cluster columns with actual query patterns

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.fact_subscription_event` (
  subscription_event_id STRING NOT NULL,
  subscription_id STRING,                -- degenerate dimension
  contract_id STRING,                    -- degenerate dimension
  event_date DATE NOT NULL,
  event_date_key INT64 NOT NULL,
  user_key INT64 NOT NULL,
  geo_key INT64,
  plan_key INT64,
  term_key INT64,
  partner_store_key INT64,
  promotion_key INT64,
  payment_method_key INT64,
  currency_key INT64,
  voucher_key INT64,
  status_key INT64,
  price_amount NUMERIC,
  discount_amount NUMERIC,
  net_amount NUMERIC,
  months_purchased INT64,
  signup_count INT64,
  etl_inserted_ts TIMESTAMP,
  etl_batch_id STRING
)
PARTITION BY event_date
CLUSTER BY user_key, plan_key, geo_key, promotion_key;

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.fact_subscription_monthly_snapshot` (
  snapshot_id STRING NOT NULL,
  subscription_id STRING,                -- degenerate dimension
  snapshot_month_start DATE NOT NULL,
  month_start_date_key INT64 NOT NULL,
  user_key INT64 NOT NULL,
  geo_key INT64,
  plan_key INT64,
  term_key INT64,
  status_key INT64,
  active_flag BOOL,
  active_subscriptions INT64,
  mrr_amount NUMERIC,
  tenure_months INT64,
  etl_inserted_ts TIMESTAMP,
  etl_batch_id STRING
)
PARTITION BY snapshot_month_start
CLUSTER BY geo_key, plan_key, user_key;

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.fact_plan_change` (
  plan_change_id STRING NOT NULL,
  subscription_id STRING,                -- degenerate dimension
  change_date DATE NOT NULL,
  change_date_key INT64 NOT NULL,
  user_key INT64 NOT NULL,
  geo_key INT64,
  from_plan_key INT64,
  to_plan_key INT64,
  device_key INT64,
  promotion_key INT64,
  status_key INT64,
  delta_mrr NUMERIC,
  churn_flag BOOL,
  change_count INT64,
  etl_inserted_ts TIMESTAMP,
  etl_batch_id STRING
)
PARTITION BY change_date
CLUSTER BY user_key, from_plan_key, to_plan_key;

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.fact_voucher_sale` (
  voucher_sale_id STRING NOT NULL,
  voucher_code STRING,                   -- degenerate dimension
  sale_date DATE NOT NULL,
  sale_date_key INT64 NOT NULL,
  prospect_key INT64,
  geo_key INT64,
  partner_store_key INT64,
  voucher_key INT64,
  promotion_key INT64,
  voucher_sale_count INT64,
  voucher_price_amount NUMERIC,
  etl_inserted_ts TIMESTAMP,
  etl_batch_id STRING
)
PARTITION BY sale_date
CLUSTER BY partner_store_key, geo_key, voucher_key;

-- accumulating snapshot
CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.fact_voucher_lifecycle` (
  voucher_key INT64 NOT NULL,
  voucher_code STRING,                   -- degenerate dimension
  sale_date DATE,
  sale_date_key INT64,
  activation_date DATE,
  activation_date_key INT64,
  conversion_date DATE,
  conversion_date_key INT64,
  prospect_key INT64,
  geo_key INT64,
  partner_store_key INT64,
  promotion_key INT64,
  status_key INT64,
  converted_subscription_id STRING,      -- degenerate dimension
  lag_sale_to_activation_days INT64,
  lag_activation_to_conversion_days INT64,
  is_activated_flag BOOL,
  is_converted_flag BOOL,
  etl_inserted_ts TIMESTAMP,
  etl_updated_ts TIMESTAMP,              -- accumulating snapshot needs update tracking
  etl_batch_id STRING
)
-- Partition by sale_date (or activation_date) depending on query patterns
PARTITION BY sale_date
CLUSTER BY partner_store_key, geo_key, status_key;

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.fact_viewing_session` (
  session_id STRING NOT NULL,
  start_ts TIMESTAMP NOT NULL,
  end_ts TIMESTAMP,
  start_date DATE NOT NULL,
  start_date_key INT64 NOT NULL,
  start_time_key INT64,
  user_key INT64 NOT NULL,
  profile_key INT64,
  geo_key INT64,
  plan_key INT64,
  device_key INT64,
  content_key INT64,
  status_key INT64,
  watch_seconds INT64,
  session_count INT64,
  concurrent_stream_flag BOOL,           -- for fraud detection
  etl_inserted_ts TIMESTAMP,
  etl_batch_id STRING
)
PARTITION BY start_date
CLUSTER BY user_key, profile_key, content_key, geo_key;

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.fact_content_tx` (
  tx_id STRING NOT NULL,
  tx_ts TIMESTAMP NOT NULL,
  tx_date DATE NOT NULL,
  tx_date_key INT64 NOT NULL,
  tx_time_key INT64,
  user_key INT64 NOT NULL,
  profile_key INT64,
  geo_key INT64,
  device_key INT64,
  content_key INT64,
  rights_holder_key INT64,
  promotion_key INT64,
  payment_method_key INT64,
  currency_key INT64,
  status_key INT64,
  gross_amount NUMERIC,
  net_amount NUMERIC,
  royalty_amount NUMERIC,
  tx_count INT64,
  etl_inserted_ts TIMESTAMP,
  etl_batch_id STRING
)
PARTITION BY tx_date
CLUSTER BY user_key, content_key, rights_holder_key, geo_key;

-- factless
CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.fact_referral_edge` (
  edge_id STRING NOT NULL,
  referral_date DATE NOT NULL,
  referral_date_key INT64 NOT NULL,
  referrer_user_key INT64 NOT NULL,
  referred_user_key INT64 NOT NULL,
  promotion_key INT64,
  referral_count INT64,
  etl_inserted_ts TIMESTAMP,
  etl_batch_id STRING
)
PARTITION BY referral_date
CLUSTER BY referrer_user_key, referred_user_key;

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.fact_referral_bonus_tx` (
  bonus_tx_id STRING NOT NULL,
  bonus_date DATE NOT NULL,
  bonus_date_key INT64 NOT NULL,
  beneficiary_user_key INT64 NOT NULL,
  originating_user_key INT64,
  depth_key INT64,
  promotion_key INT64,
  currency_key INT64,
  bonus_amount NUMERIC,
  bonus_count INT64,
  etl_inserted_ts TIMESTAMP,
  etl_batch_id STRING
)
PARTITION BY bonus_date
CLUSTER BY beneficiary_user_key, depth_key;

-- factless
CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.fact_device_link` (
  link_event_id STRING NOT NULL,
  event_date DATE NOT NULL,
  event_date_key INT64 NOT NULL,
  user_key INT64 NOT NULL,
  device_key INT64 NOT NULL,
  status_key INT64,
  link_count INT64,
  etl_inserted_ts TIMESTAMP,
  etl_batch_id STRING
)
PARTITION BY event_date
CLUSTER BY user_key, device_key;

-- factless
CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.fact_profile_event` (
  profile_event_id STRING NOT NULL,
  event_date DATE NOT NULL,
  event_date_key INT64 NOT NULL,
  user_key INT64 NOT NULL,
  profile_key INT64 NOT NULL,
  geo_key INT64,
  status_key INT64,
  profile_event_count INT64,
  etl_inserted_ts TIMESTAMP,
  etl_batch_id STRING
)
PARTITION BY event_date
CLUSTER BY user_key, profile_key;

-- external data
-- Derived metric (calculated at query time, not stored):
--   market_coverage_pct = SUM(active_subscriptions) / population
--   Requires JOIN with fact_subscription_monthly_snapshot by geo_key + date
CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.YOUR_DATASET.fact_region_demographics` (
  record_id STRING NOT NULL,
  year_date DATE NOT NULL,
  year_date_key INT64 NOT NULL,
  geo_key INT64 NOT NULL,
  status_key INT64,
  population INT64,
  target_demo_population INT64,
  households_count INT64,
  internet_penetration_pct NUMERIC,
  etl_inserted_ts TIMESTAMP,
  etl_batch_id STRING
)
PARTITION BY year_date
CLUSTER BY geo_key;

