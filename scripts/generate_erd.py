#!/usr/bin/env python3
"""
ERD Generator for Netflix Data Warehouse (BigQuery)

Two methods supported:
1. QuickDBD format export (manual visual tool)
2. bigquery-erd package (automated, requires column descriptions)

Usage:
    python generate_erd.py --method quickdbd > quickdbd_schema.txt
    python generate_erd.py --method metadata > schema_metadata.sql
    
References:
- QuickDBD: https://www.quickdatabasediagrams.com/
- bigquery-erd: https://pypi.org/project/bigquery-erd/
- Article: https://medium.com/javarevisited/create-an-erd-from-big-query-dataset-tables-hack-24e4b6c10eea
"""

import argparse

# Netflix DW Schema Definition
SCHEMA = {
    "dimensions": {
        "dim_date": {
            "columns": [
                ("date_key", "INT64", "PK"),
                ("calendar_date", "DATE"),
                ("year", "INT64"),
                ("quarter", "INT64"),
                ("month", "INT64"),
                ("day", "INT64"),
                ("day_of_week", "INT64"),
                ("month_start_flag", "BOOL"),
                ("month_end_flag", "BOOL"),
            ]
        },
        "dim_time": {
            "columns": [
                ("time_key", "INT64", "PK"),
                ("hhmmss", "STRING"),
                ("hour", "INT64"),
                ("minute", "INT64"),
                ("second", "INT64"),
                ("day_part", "STRING"),
            ]
        },
        "dim_user": {
            "columns": [
                ("user_key", "INT64", "PK"),
                ("user_id", "STRING"),
                ("effective_start_ts", "TIMESTAMP"),
                ("effective_end_ts", "TIMESTAMP"),
                ("is_current", "BOOL"),
                ("signup_date_key", "INT64", "FK", "dim_date.date_key"),
                ("current_geo_key", "INT64", "FK", "dim_geography.geo_key"),
                ("signup_channel", "STRING"),
                ("email_hash", "STRING"),
            ]
        },
        "dim_profile": {
            "columns": [
                ("profile_key", "INT64", "PK"),
                ("profile_id", "STRING"),
                ("user_id", "STRING"),
                ("effective_start_ts", "TIMESTAMP"),
                ("effective_end_ts", "TIMESTAMP"),
                ("is_current", "BOOL"),
                ("age_band", "STRING"),
                ("gender", "STRING"),
                ("habitual_city", "STRING"),
                ("is_family_default", "BOOL"),
            ]
        },
        "dim_geography": {
            "columns": [
                ("geo_key", "INT64", "PK"),
                ("country_code", "STRING"),
                ("country", "STRING"),
                ("region", "STRING"),
                ("city", "STRING"),
                ("latitude_bucket", "STRING"),
                ("longitude_bucket", "STRING"),
            ]
        },
        "dim_plan": {
            "columns": [
                ("plan_key", "INT64", "PK"),
                ("plan_code", "STRING"),
                ("effective_start_ts", "TIMESTAMP"),
                ("effective_end_ts", "TIMESTAMP"),
                ("is_current", "BOOL"),
                ("plan_name", "STRING"),
                ("included_channels_cnt", "INT64"),
                ("included_titles_cnt", "INT64"),
            ]
        },
        "dim_term": {
            "columns": [
                ("term_key", "INT64", "PK"),
                ("term_months", "INT64"),
            ]
        },
        "dim_device": {
            "columns": [
                ("device_key", "INT64", "PK"),
                ("device_id", "STRING"),
                ("device_type", "STRING"),
                ("os", "STRING"),
                ("app_version", "STRING"),
            ]
        },
        "dim_content": {
            "columns": [
                ("content_key", "INT64", "PK"),
                ("content_id", "STRING"),
                ("title", "STRING"),
                ("content_type", "STRING"),
                ("genre", "STRING"),
                ("release_year", "INT64"),
            ]
        },
        "dim_rights_holder": {
            "columns": [
                ("rights_holder_key", "INT64", "PK"),
                ("rights_holder_id", "STRING"),
                ("name", "STRING"),
                ("contract_type", "STRING"),
            ]
        },
        "dim_partner_store": {
            "columns": [
                ("partner_store_key", "INT64", "PK"),
                ("store_id", "STRING"),
                ("store_name", "STRING"),
                ("chain", "STRING"),
                ("geo_key", "INT64", "FK", "dim_geography.geo_key"),
            ]
        },
        "dim_promotion": {
            "columns": [
                ("promotion_key", "INT64", "PK"),
                ("promotion_code", "STRING"),
                ("promotion_type", "STRING"),
                ("description", "STRING"),
            ]
        },
        "dim_payment_method": {
            "columns": [
                ("payment_method_key", "INT64", "PK"),
                ("payment_method_code", "STRING"),
                ("provider", "STRING"),
            ]
        },
        "dim_currency": {
            "columns": [
                ("currency_key", "INT64", "PK"),
                ("iso_currency_code", "STRING"),
                ("currency_name", "STRING"),
            ]
        },
        "dim_voucher": {
            "columns": [
                ("voucher_key", "INT64", "PK"),
                ("voucher_code", "STRING"),
                ("voucher_type", "STRING"),
                ("nominal_term_months", "INT64"),
            ]
        },
        "dim_referral_depth": {
            "columns": [
                ("depth_key", "INT64", "PK"),
                ("depth", "INT64"),
            ]
        },
        "dim_status": {
            "columns": [
                ("status_key", "INT64", "PK"),
                ("status_code", "STRING"),
                ("status_group", "STRING"),
            ]
        },
        "dim_prospect": {
            "columns": [
                ("prospect_key", "INT64", "PK"),
                ("lead_id", "STRING"),
                ("phone_hash", "STRING"),
                ("effective_start_ts", "TIMESTAMP"),
                ("effective_end_ts", "TIMESTAMP"),
                ("is_current", "BOOL"),
                ("age_band", "STRING"),
                ("gender", "STRING"),
                ("city_at_sale", "STRING"),
                ("geo_key", "INT64", "FK", "dim_geography.geo_key"),
            ]
        },
    },
    "facts": {
        "fact_subscription_event": {
            "columns": [
                ("subscription_event_id", "STRING", "PK"),
                ("subscription_id", "STRING"),
                ("contract_id", "STRING"),
                ("event_date", "DATE"),
                ("event_date_key", "INT64", "FK", "dim_date.date_key"),
                ("user_key", "INT64", "FK", "dim_user.user_key"),
                ("geo_key", "INT64", "FK", "dim_geography.geo_key"),
                ("plan_key", "INT64", "FK", "dim_plan.plan_key"),
                ("term_key", "INT64", "FK", "dim_term.term_key"),
                ("partner_store_key", "INT64", "FK", "dim_partner_store.partner_store_key"),
                ("promotion_key", "INT64", "FK", "dim_promotion.promotion_key"),
                ("payment_method_key", "INT64", "FK", "dim_payment_method.payment_method_key"),
                ("currency_key", "INT64", "FK", "dim_currency.currency_key"),
                ("voucher_key", "INT64", "FK", "dim_voucher.voucher_key"),
                ("status_key", "INT64", "FK", "dim_status.status_key"),
                ("price_amount", "NUMERIC"),
                ("discount_amount", "NUMERIC"),
                ("net_amount", "NUMERIC"),
                ("months_purchased", "INT64"),
                ("signup_count", "INT64"),
            ]
        },
        "fact_subscription_monthly_snapshot": {
            "columns": [
                ("snapshot_id", "STRING", "PK"),
                ("subscription_id", "STRING"),
                ("snapshot_month_start", "DATE"),
                ("month_start_date_key", "INT64", "FK", "dim_date.date_key"),
                ("user_key", "INT64", "FK", "dim_user.user_key"),
                ("geo_key", "INT64", "FK", "dim_geography.geo_key"),
                ("plan_key", "INT64", "FK", "dim_plan.plan_key"),
                ("term_key", "INT64", "FK", "dim_term.term_key"),
                ("status_key", "INT64", "FK", "dim_status.status_key"),
                ("active_flag", "BOOL"),
                ("active_subscriptions", "INT64"),
                ("mrr_amount", "NUMERIC"),
                ("tenure_months", "INT64"),
            ]
        },
        "fact_plan_change": {
            "columns": [
                ("plan_change_id", "STRING", "PK"),
                ("subscription_id", "STRING"),
                ("change_date", "DATE"),
                ("change_date_key", "INT64", "FK", "dim_date.date_key"),
                ("user_key", "INT64", "FK", "dim_user.user_key"),
                ("geo_key", "INT64", "FK", "dim_geography.geo_key"),
                ("from_plan_key", "INT64", "FK", "dim_plan.plan_key"),
                ("to_plan_key", "INT64", "FK", "dim_plan.plan_key"),
                ("device_key", "INT64", "FK", "dim_device.device_key"),
                ("promotion_key", "INT64", "FK", "dim_promotion.promotion_key"),
                ("status_key", "INT64", "FK", "dim_status.status_key"),
                ("delta_mrr", "NUMERIC"),
                ("churn_flag", "BOOL"),
                ("change_count", "INT64"),
            ]
        },
        "fact_voucher_sale": {
            "columns": [
                ("voucher_sale_id", "STRING", "PK"),
                ("voucher_code", "STRING"),
                ("sale_date", "DATE"),
                ("sale_date_key", "INT64", "FK", "dim_date.date_key"),
                ("prospect_key", "INT64", "FK", "dim_prospect.prospect_key"),
                ("geo_key", "INT64", "FK", "dim_geography.geo_key"),
                ("partner_store_key", "INT64", "FK", "dim_partner_store.partner_store_key"),
                ("voucher_key", "INT64", "FK", "dim_voucher.voucher_key"),
                ("promotion_key", "INT64", "FK", "dim_promotion.promotion_key"),
                ("voucher_sale_count", "INT64"),
                ("voucher_price_amount", "NUMERIC"),
            ]
        },
        "fact_voucher_lifecycle": {
            "columns": [
                ("voucher_key", "INT64", "PK,FK", "dim_voucher.voucher_key"),
                ("voucher_code", "STRING"),
                ("sale_date", "DATE"),
                ("sale_date_key", "INT64", "FK", "dim_date.date_key"),
                ("activation_date", "DATE"),
                ("activation_date_key", "INT64", "FK", "dim_date.date_key"),
                ("conversion_date", "DATE"),
                ("conversion_date_key", "INT64", "FK", "dim_date.date_key"),
                ("prospect_key", "INT64", "FK", "dim_prospect.prospect_key"),
                ("geo_key", "INT64", "FK", "dim_geography.geo_key"),
                ("partner_store_key", "INT64", "FK", "dim_partner_store.partner_store_key"),
                ("promotion_key", "INT64", "FK", "dim_promotion.promotion_key"),
                ("status_key", "INT64", "FK", "dim_status.status_key"),
                ("converted_subscription_id", "STRING"),
                ("lag_sale_to_activation_days", "INT64"),
                ("lag_activation_to_conversion_days", "INT64"),
                ("is_activated_flag", "BOOL"),
                ("is_converted_flag", "BOOL"),
            ]
        },
        "fact_viewing_session": {
            "columns": [
                ("session_id", "STRING", "PK"),
                ("start_ts", "TIMESTAMP"),
                ("end_ts", "TIMESTAMP"),
                ("start_date", "DATE"),
                ("start_date_key", "INT64", "FK", "dim_date.date_key"),
                ("start_time_key", "INT64", "FK", "dim_time.time_key"),
                ("user_key", "INT64", "FK", "dim_user.user_key"),
                ("profile_key", "INT64", "FK", "dim_profile.profile_key"),
                ("geo_key", "INT64", "FK", "dim_geography.geo_key"),
                ("plan_key", "INT64", "FK", "dim_plan.plan_key"),
                ("device_key", "INT64", "FK", "dim_device.device_key"),
                ("content_key", "INT64", "FK", "dim_content.content_key"),
                ("status_key", "INT64", "FK", "dim_status.status_key"),
                ("watch_seconds", "INT64"),
                ("session_count", "INT64"),
                ("concurrent_stream_flag", "BOOL"),
            ]
        },
        "fact_content_tx": {
            "columns": [
                ("tx_id", "STRING", "PK"),
                ("tx_ts", "TIMESTAMP"),
                ("tx_date", "DATE"),
                ("tx_date_key", "INT64", "FK", "dim_date.date_key"),
                ("tx_time_key", "INT64", "FK", "dim_time.time_key"),
                ("user_key", "INT64", "FK", "dim_user.user_key"),
                ("profile_key", "INT64", "FK", "dim_profile.profile_key"),
                ("geo_key", "INT64", "FK", "dim_geography.geo_key"),
                ("device_key", "INT64", "FK", "dim_device.device_key"),
                ("content_key", "INT64", "FK", "dim_content.content_key"),
                ("rights_holder_key", "INT64", "FK", "dim_rights_holder.rights_holder_key"),
                ("promotion_key", "INT64", "FK", "dim_promotion.promotion_key"),
                ("payment_method_key", "INT64", "FK", "dim_payment_method.payment_method_key"),
                ("currency_key", "INT64", "FK", "dim_currency.currency_key"),
                ("status_key", "INT64", "FK", "dim_status.status_key"),
                ("gross_amount", "NUMERIC"),
                ("net_amount", "NUMERIC"),
                ("royalty_amount", "NUMERIC"),
                ("tx_count", "INT64"),
            ]
        },
        "fact_referral_edge": {
            "columns": [
                ("edge_id", "STRING", "PK"),
                ("referral_date", "DATE"),
                ("referral_date_key", "INT64", "FK", "dim_date.date_key"),
                ("referrer_user_key", "INT64", "FK", "dim_user.user_key"),
                ("referred_user_key", "INT64", "FK", "dim_user.user_key"),
                ("promotion_key", "INT64", "FK", "dim_promotion.promotion_key"),
                ("referral_count", "INT64"),
            ]
        },
        "fact_referral_bonus_tx": {
            "columns": [
                ("bonus_tx_id", "STRING", "PK"),
                ("bonus_date", "DATE"),
                ("bonus_date_key", "INT64", "FK", "dim_date.date_key"),
                ("beneficiary_user_key", "INT64", "FK", "dim_user.user_key"),
                ("originating_user_key", "INT64", "FK", "dim_user.user_key"),
                ("depth_key", "INT64", "FK", "dim_referral_depth.depth_key"),
                ("promotion_key", "INT64", "FK", "dim_promotion.promotion_key"),
                ("currency_key", "INT64", "FK", "dim_currency.currency_key"),
                ("bonus_amount", "NUMERIC"),
                ("bonus_count", "INT64"),
            ]
        },
        "fact_device_link": {
            "columns": [
                ("link_event_id", "STRING", "PK"),
                ("event_date", "DATE"),
                ("event_date_key", "INT64", "FK", "dim_date.date_key"),
                ("user_key", "INT64", "FK", "dim_user.user_key"),
                ("device_key", "INT64", "FK", "dim_device.device_key"),
                ("status_key", "INT64", "FK", "dim_status.status_key"),
                ("link_count", "INT64"),
            ]
        },
        "fact_profile_event": {
            "columns": [
                ("profile_event_id", "STRING", "PK"),
                ("event_date", "DATE"),
                ("event_date_key", "INT64", "FK", "dim_date.date_key"),
                ("user_key", "INT64", "FK", "dim_user.user_key"),
                ("profile_key", "INT64", "FK", "dim_profile.profile_key"),
                ("geo_key", "INT64", "FK", "dim_geography.geo_key"),
                ("status_key", "INT64", "FK", "dim_status.status_key"),
                ("profile_event_count", "INT64"),
            ]
        },
        "fact_region_demographics": {
            "columns": [
                ("record_id", "STRING", "PK"),
                ("year_date", "DATE"),
                ("year_date_key", "INT64", "FK", "dim_date.date_key"),
                ("geo_key", "INT64", "FK", "dim_geography.geo_key"),
                ("status_key", "INT64", "FK", "dim_status.status_key"),
                ("population", "INT64"),
                ("target_demo_population", "INT64"),
                ("households_count", "INT64"),
                ("internet_penetration_pct", "NUMERIC"),
            ]
        },
    }
}


def generate_quickdbd_format():
    """Generate QuickDBD format for visual ERD tool."""
    output = []
    output.append("# Netflix Data Warehouse ERD")
    output.append("# Paste this into https://www.quickdatabasediagrams.com/")
    output.append("#")
    output.append("# ========== DIMENSIONS ==========")
    output.append("")
    
    # Generate dimensions
    for table_name, table_def in SCHEMA["dimensions"].items():
        output.append(f"{table_name}")
        output.append("-")
        for col in table_def["columns"]:
            col_name, col_type = col[0], col[1]
            suffix = ""
            if len(col) >= 3 and "PK" in col[2]:
                suffix = " PK"
            if len(col) >= 4:
                # FK reference
                suffix += f" FK >- {col[3]}"
            elif len(col) >= 3 and "FK" in col[2] and len(col) > 3:
                suffix += f" FK >- {col[3]}"
            output.append(f"{col_name} {col_type}{suffix}")
        output.append("")
    
    output.append("# ========== FACTS ==========")
    output.append("")
    
    # Generate facts
    for table_name, table_def in SCHEMA["facts"].items():
        output.append(f"{table_name}")
        output.append("-")
        for col in table_def["columns"]:
            col_name, col_type = col[0], col[1]
            suffix = ""
            if len(col) >= 3 and "PK" in col[2]:
                suffix = " PK"
            if len(col) >= 4:
                suffix += f" FK >- {col[3]}"
            output.append(f"{col_name} {col_type}{suffix}")
        output.append("")
    
    return "\n".join(output)


def generate_bq_metadata_queries(project_id="YOUR_PROJECT", dataset="netflix_dw"):
    """Generate BigQuery queries to extract schema metadata."""
    output = []
    output.append(f"-- Query 1: Get all tables in dataset")
    output.append(f"""SELECT table_name 
FROM `{project_id}.{dataset}.INFORMATION_SCHEMA.TABLES`
ORDER BY table_name;
""")
    
    output.append(f"-- Query 2: Get columns for all tables")
    output.append(f"""SELECT 
  table_name,
  column_name,
  data_type,
  is_nullable
FROM `{project_id}.{dataset}.INFORMATION_SCHEMA.COLUMNS`
ORDER BY table_name, ordinal_position;
""")
    
    output.append(f"-- Query 3: Get column descriptions (for bigquery-erd)")
    output.append(f"""SELECT 
  table_name,
  column_name,
  description
FROM `{project_id}.{dataset}.INFORMATION_SCHEMA.COLUMN_FIELD_PATHS`
WHERE description IS NOT NULL
ORDER BY table_name, column_name;
""")
    
    return "\n".join(output)


def generate_bq_erd_descriptions():
    """Generate SQL to add FK descriptions for bigquery-erd package."""
    output = []
    output.append("-- SQL statements to add FK descriptions for bigquery-erd")
    output.append("-- Run these to enable automatic ERD generation")
    output.append("-- Reference: https://pypi.org/project/bigquery-erd/")
    output.append("")
    
    all_tables = {**SCHEMA["dimensions"], **SCHEMA["facts"]}
    
    for table_name, table_def in all_tables.items():
        for col in table_def["columns"]:
            if len(col) >= 4:  # Has FK reference
                col_name = col[0]
                fk_ref = col[3]  # e.g., "dim_date.date_key"
                output.append(f"-- {table_name}.{col_name} -> {fk_ref}")
                output.append(f"""ALTER TABLE `YOUR_PROJECT.netflix_dw.{table_name}`
ALTER COLUMN {col_name} SET OPTIONS (description='-> {fk_ref}');
""")
    
    return "\n".join(output)


def generate_erd_image(output_file="netflix_dw_erd.png"):
    """
    Generate ERD image from built-in schema using graphviz.
    Requires: pip install graphviz
              brew install graphviz
    """
    try:
        import graphviz
        
        # Build DOT content from built-in schema
        dot_lines = [
            'digraph ERD {',
            '  graph [rankdir=LR, splines=ortho, nodesep=0.8];',
            '  node [shape=none, fontname="Helvetica", fontsize=10];',
            '  edge [arrowhead=crow, arrowtail=none];',
            ''
        ]
        
        # Add dimension tables
        for table_name, table_def in SCHEMA["dimensions"].items():
            cols_html = "".join([
                f'<TR><TD ALIGN="LEFT" PORT="{c[0]}">{c[0]}</TD><TD ALIGN="LEFT">{c[1]}</TD></TR>'
                for c in table_def["columns"]
            ])
            dot_lines.append(f'  {table_name} [label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0">')
            dot_lines.append(f'    <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>{table_name}</B></TD></TR>')
            dot_lines.append(f'    {cols_html}')
            dot_lines.append(f'  </TABLE>>];')
        
        # Add fact tables
        for table_name, table_def in SCHEMA["facts"].items():
            cols_html = "".join([
                f'<TR><TD ALIGN="LEFT" PORT="{c[0]}">{c[0]}</TD><TD ALIGN="LEFT">{c[1]}</TD></TR>'
                for c in table_def["columns"]
            ])
            dot_lines.append(f'  {table_name} [label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0">')
            dot_lines.append(f'    <TR><TD COLSPAN="2" BGCOLOR="lightyellow"><B>{table_name}</B></TD></TR>')
            dot_lines.append(f'    {cols_html}')
            dot_lines.append(f'  </TABLE>>];')
        
        # Add relationships (FK -> PK)
        for table_name, table_def in {**SCHEMA["dimensions"], **SCHEMA["facts"]}.items():
            for col in table_def["columns"]:
                if len(col) >= 4 and "FK" in col[2]:
                    # col[3] is like "dim_date.date_key"
                    target_table, target_col = col[3].split(".")
                    dot_lines.append(f'  {table_name}:{col[0]} -> {target_table}:{target_col};')
        
        dot_lines.append('}')
        dot_content = "\n".join(dot_lines)
        
        # Determine output format
        output_base = output_file.rsplit('.', 1)[0]
        output_format = output_file.rsplit('.', 1)[1] if '.' in output_file else 'png'
        
        print(f"Generating ERD with {len(SCHEMA['dimensions'])} dimensions, {len(SCHEMA['facts'])} facts...")
        print(f"Rendering to: {output_file}")
        
        graph = graphviz.Source(dot_content)
        graph.render(output_base, format=output_format, cleanup=True)
        
        print(f"ERD saved to {output_file}")
        return True
        
    except ImportError as e:
        print("Error: graphviz package not installed. Run:")
        print("  pip install graphviz")
        print("  brew install graphviz")
        print(f"Details: {e}")
        return False
    except Exception as e:
        print(f"Error generating ERD: {e}")
        print("Make sure graphviz is installed: brew install graphviz")
        return False


def generate_star_schema_diagrams(output_dir="scripts"):
    """
    Generate individual star schema diagrams for each fact table.
    Each diagram shows one fact table in the center with its connected dimensions.
    """
    try:
        import graphviz
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        
        generated_files = []
        
        for fact_name, fact_def in SCHEMA["facts"].items():
            # Find all dimensions this fact connects to
            connected_dims = set()
            fk_relations = []
            
            for col in fact_def["columns"]:
                if len(col) >= 4 and "FK" in col[2]:
                    target_table, target_col = col[3].split(".")
                    connected_dims.add(target_table)
                    fk_relations.append((col[0], target_table, target_col))
            
            # Build DOT for this star schema
            dot_lines = [
                'digraph star_schema {',
                '  graph [rankdir=LR, splines=ortho, nodesep=0.5, ranksep=1.5];',
                '  node [shape=none, fontname="Helvetica", fontsize=11];',
                '  edge [arrowhead=crow, arrowtail=none, color="#666666"];',
                ''
            ]
            
            # Add fact table (center, yellow)
            fact_cols_html = "".join([
                f'<TR><TD ALIGN="LEFT" PORT="{c[0]}">{c[0]}</TD><TD ALIGN="LEFT">{c[1]}</TD></TR>'
                for c in fact_def["columns"]
            ])
            dot_lines.append(f'  {fact_name} [label=<<TABLE BORDER="2" CELLBORDER="0" CELLSPACING="0" BGCOLOR="#FFFACD">')
            dot_lines.append(f'    <TR><TD COLSPAN="2" BGCOLOR="#FFD700"><B>{fact_name}</B></TD></TR>')
            dot_lines.append(f'    {fact_cols_html}')
            dot_lines.append(f'  </TABLE>>];')
            
            # Add connected dimension tables (blue)
            for dim_name in sorted(connected_dims):
                if dim_name in SCHEMA["dimensions"]:
                    dim_def = SCHEMA["dimensions"][dim_name]
                    dim_cols_html = "".join([
                        f'<TR><TD ALIGN="LEFT" PORT="{c[0]}">{c[0]}</TD><TD ALIGN="LEFT">{c[1]}</TD></TR>'
                        for c in dim_def["columns"]
                    ])
                    dot_lines.append(f'  {dim_name} [label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" BGCOLOR="#E6F3FF">')
                    dot_lines.append(f'    <TR><TD COLSPAN="2" BGCOLOR="#87CEEB"><B>{dim_name}</B></TD></TR>')
                    dot_lines.append(f'    {dim_cols_html}')
                    dot_lines.append(f'  </TABLE>>];')
            
            # Add FK relationships
            for fk_col, target_table, target_col in fk_relations:
                dot_lines.append(f'  {fact_name}:{fk_col} -> {target_table}:{target_col};')
            
            dot_lines.append('}')
            dot_content = "\n".join(dot_lines)
            
            # Render
            output_base = os.path.join(output_dir, f"star_{fact_name}")
            graph = graphviz.Source(dot_content)
            graph.render(output_base, format='png', cleanup=True)
            
            output_file = f"{output_base}.png"
            generated_files.append(output_file)
            print(f"  ✓ {fact_name} → {len(connected_dims)} dims → {output_file}")
        
        print(f"\nGenerated {len(generated_files)} star schema diagrams in {output_dir}/")
        return generated_files
        
    except ImportError as e:
        print("Error: graphviz package not installed. Run:")
        print("  pip install graphviz")
        print("  brew install graphviz")
        print(f"Details: {e}")
        return []
    except Exception as e:
        print(f"Error generating star schemas: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description="Generate ERD for Netflix DW")
    parser.add_argument(
        "--method", 
        choices=["quickdbd", "metadata", "descriptions", "bigquery-erd", "star-schemas", "all"],
        default="all",
        help="Output format: star-schemas generates one diagram per fact table"
    )
    parser.add_argument(
        "--project", 
        default="project-534688f2-c3a9-4bff-95a",
        help="GCP Project ID"
    )
    parser.add_argument(
        "--output", 
        default="scripts",
        help="Output file (for bigquery-erd) or directory (for star-schemas)"
    )
    
    args = parser.parse_args()
    
    if args.method == "quickdbd":
        print(generate_quickdbd_format())
    elif args.method == "metadata":
        print(generate_bq_metadata_queries(args.project))
    elif args.method == "descriptions":
        print(generate_bq_erd_descriptions())
    elif args.method == "bigquery-erd":
        output = args.output if args.output.endswith('.png') else f"{args.output}/netflix_dw_erd.png"
        generate_erd_image(output)
    elif args.method == "star-schemas":
        print("Generating individual star schema diagrams...")
        generate_star_schema_diagrams(args.output)
    else:
        print("=" * 60)
        print("QUICKDBD FORMAT (paste into quickdatabasediagrams.com)")
        print("=" * 60)
        print(generate_quickdbd_format())
        print("\n")
        print("=" * 60)
        print("BIGQUERY METADATA QUERIES")
        print("=" * 60)
        print(generate_bq_metadata_queries(args.project))
        print("\n")
        print("=" * 60)
        print("BIGQUERY-ERD COLUMN DESCRIPTIONS")
        print("=" * 60)
        print(generate_bq_erd_descriptions())


if __name__ == "__main__":
    main()

