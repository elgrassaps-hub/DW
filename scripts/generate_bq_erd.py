#!/usr/bin/env python3
"""
Generate ERD diagrams from actual BigQuery dataset schemas.
Queries BigQuery INFORMATION_SCHEMA to get real table structures.

Usage:
    python scripts/generate_bq_erd.py --output BQ_erd_generated
"""

import argparse
import os

PROJECT_ID = "project-534688f2-c3a9-4bff-95a"
DATASET_ID = "netflix_dw"


def fetch_bq_schemas(project_id, dataset_id):
    """Fetch all table schemas from BigQuery."""
    from google.cloud import bigquery
    
    client = bigquery.Client(project=project_id)
    
    # Get all tables
    query = f"""
    SELECT 
        table_name,
        column_name,
        data_type,
        is_nullable,
        ordinal_position
    FROM `{project_id}.{dataset_id}.INFORMATION_SCHEMA.COLUMNS`
    ORDER BY table_name, ordinal_position
    """
    
    results = client.query(query).result()
    
    # Group by table
    tables = {}
    for row in results:
        table_name = row.table_name
        if table_name not in tables:
            tables[table_name] = []
        tables[table_name].append({
            "name": row.column_name,
            "type": row.data_type,
            "nullable": row.is_nullable == "YES"
        })
    
    return tables


def generate_table_erd(table_name, columns, output_dir, is_fact=False):
    """Generate ERD for a single table."""
    import graphviz
    
    # Determine colors
    if is_fact:
        header_color = "#FFD700"  # Gold
        bg_color = "#FFFACD"      # Light yellow
    else:
        header_color = "#87CEEB"  # Sky blue
        bg_color = "#E6F3FF"      # Light blue
    
    dot_lines = [
        'digraph table_schema {',
        '  graph [rankdir=TB];',
        '  node [shape=none, fontname="Helvetica", fontsize=11];',
        ''
    ]
    
    # Build table HTML
    cols_html = ""
    for col in columns:
        nullable = "NULL" if col["nullable"] else "NOT NULL"
        cols_html += f'<TR><TD ALIGN="LEFT">{col["name"]}</TD><TD ALIGN="LEFT">{col["type"]}</TD><TD ALIGN="LEFT">{nullable}</TD></TR>'
    
    dot_lines.append(f'  {table_name} [label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" BGCOLOR="{bg_color}">')
    dot_lines.append(f'    <TR><TD COLSPAN="3" BGCOLOR="{header_color}"><B>{table_name}</B></TD></TR>')
    dot_lines.append(f'    <TR><TD BGCOLOR="#DDDDDD"><B>Column</B></TD><TD BGCOLOR="#DDDDDD"><B>Type</B></TD><TD BGCOLOR="#DDDDDD"><B>Nullable</B></TD></TR>')
    dot_lines.append(f'    {cols_html}')
    dot_lines.append(f'  </TABLE>>];')
    dot_lines.append('}')
    
    dot_content = "\n".join(dot_lines)
    
    # Render
    output_base = os.path.join(output_dir, table_name)
    graph = graphviz.Source(dot_content)
    graph.render(output_base, format='png', cleanup=True)
    
    return f"{output_base}.png"


def generate_full_erd(tables, output_dir):
    """Generate full ERD with all tables."""
    import graphviz
    
    dot_lines = [
        'digraph full_erd {',
        '  graph [rankdir=LR, splines=ortho, nodesep=0.5];',
        '  node [shape=none, fontname="Helvetica", fontsize=9];',
        '  edge [arrowhead=crow, arrowtail=none, color="#666666"];',
        ''
    ]
    
    # Separate dims and facts
    dims = {k: v for k, v in tables.items() if k.startswith("dim_")}
    facts = {k: v for k, v in tables.items() if k.startswith("fact_")}
    
    # Add dimension tables
    for table_name, columns in sorted(dims.items()):
        cols_html = "".join([
            f'<TR><TD ALIGN="LEFT" PORT="{c["name"]}">{c["name"]}</TD><TD ALIGN="LEFT">{c["type"]}</TD></TR>'
            for c in columns[:15]  # Limit columns for readability
        ])
        if len(columns) > 15:
            cols_html += f'<TR><TD COLSPAN="2">... +{len(columns)-15} more</TD></TR>'
        
        dot_lines.append(f'  {table_name} [label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" BGCOLOR="#E6F3FF">')
        dot_lines.append(f'    <TR><TD COLSPAN="2" BGCOLOR="#87CEEB"><B>{table_name}</B></TD></TR>')
        dot_lines.append(f'    {cols_html}')
        dot_lines.append(f'  </TABLE>>];')
    
    # Add fact tables
    for table_name, columns in sorted(facts.items()):
        cols_html = "".join([
            f'<TR><TD ALIGN="LEFT" PORT="{c["name"]}">{c["name"]}</TD><TD ALIGN="LEFT">{c["type"]}</TD></TR>'
            for c in columns[:20]
        ])
        if len(columns) > 20:
            cols_html += f'<TR><TD COLSPAN="2">... +{len(columns)-20} more</TD></TR>'
        
        dot_lines.append(f'  {table_name} [label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" BGCOLOR="#FFFACD">')
        dot_lines.append(f'    <TR><TD COLSPAN="2" BGCOLOR="#FFD700"><B>{table_name}</B></TD></TR>')
        dot_lines.append(f'    {cols_html}')
        dot_lines.append(f'  </TABLE>>];')
    
    # Add FK relationships (infer from _key columns)
    for fact_name, columns in facts.items():
        for col in columns:
            col_name = col["name"]
            if col_name.endswith("_key") and col_name not in ["date_key"]:
                # Try to find matching dimension
                for dim_name in dims.keys():
                    # Match dim_user -> user_key, dim_date -> date_key, etc.
                    dim_suffix = dim_name.replace("dim_", "") + "_key"
                    if col_name == dim_suffix or col_name.endswith(f"_{dim_suffix}"):
                        dot_lines.append(f'  {fact_name}:{col_name} -> {dim_name}:{col_name};')
                        break
                    # Also check direct key match
                    if col_name in [c["name"] for c in dims[dim_name]]:
                        dot_lines.append(f'  {fact_name}:{col_name} -> {dim_name}:{col_name};')
                        break
    
    dot_lines.append('}')
    dot_content = "\n".join(dot_lines)
    
    # Render
    output_base = os.path.join(output_dir, "full_erd")
    graph = graphviz.Source(dot_content)
    graph.render(output_base, format='png', cleanup=True)
    
    return f"{output_base}.png"


def generate_star_erd(fact_name, fact_columns, all_tables, output_dir):
    """Generate star schema ERD for a single fact table."""
    import graphviz
    
    dot_lines = [
        'digraph star_schema {',
        '  graph [rankdir=LR, splines=ortho, nodesep=0.5, ranksep=1.2];',
        '  node [shape=none, fontname="Helvetica", fontsize=10];',
        '  edge [arrowhead=crow, arrowtail=none, color="#666666"];',
        ''
    ]
    
    # Find connected dimensions
    connected_dims = set()
    for col in fact_columns:
        col_name = col["name"]
        if col_name.endswith("_key"):
            for dim_name in all_tables.keys():
                if dim_name.startswith("dim_"):
                    dim_suffix = dim_name.replace("dim_", "") + "_key"
                    if col_name == dim_suffix or col_name.endswith(f"_{dim_suffix}"):
                        connected_dims.add(dim_name)
                        break
                    if col_name in [c["name"] for c in all_tables[dim_name]]:
                        connected_dims.add(dim_name)
                        break
    
    # Add fact table (center)
    cols_html = "".join([
        f'<TR><TD ALIGN="LEFT" PORT="{c["name"]}">{c["name"]}</TD><TD ALIGN="LEFT">{c["type"]}</TD></TR>'
        for c in fact_columns
    ])
    dot_lines.append(f'  {fact_name} [label=<<TABLE BORDER="2" CELLBORDER="0" CELLSPACING="0" BGCOLOR="#FFFACD">')
    dot_lines.append(f'    <TR><TD COLSPAN="2" BGCOLOR="#FFD700"><B>{fact_name}</B></TD></TR>')
    dot_lines.append(f'    {cols_html}')
    dot_lines.append(f'  </TABLE>>];')
    
    # Add connected dimensions
    for dim_name in sorted(connected_dims):
        if dim_name in all_tables:
            dim_columns = all_tables[dim_name]
            cols_html = "".join([
                f'<TR><TD ALIGN="LEFT" PORT="{c["name"]}">{c["name"]}</TD><TD ALIGN="LEFT">{c["type"]}</TD></TR>'
                for c in dim_columns
            ])
            dot_lines.append(f'  {dim_name} [label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" BGCOLOR="#E6F3FF">')
            dot_lines.append(f'    <TR><TD COLSPAN="2" BGCOLOR="#87CEEB"><B>{dim_name}</B></TD></TR>')
            dot_lines.append(f'    {cols_html}')
            dot_lines.append(f'  </TABLE>>];')
    
    # Add FK relationships
    for col in fact_columns:
        col_name = col["name"]
        if col_name.endswith("_key"):
            for dim_name in connected_dims:
                dim_suffix = dim_name.replace("dim_", "") + "_key"
                if col_name == dim_suffix or col_name.endswith(f"_{dim_suffix}"):
                    dot_lines.append(f'  {fact_name}:{col_name} -> {dim_name}:{col_name};')
                    break
                if col_name in [c["name"] for c in all_tables[dim_name]]:
                    dot_lines.append(f'  {fact_name}:{col_name} -> {dim_name}:{col_name};')
                    break
    
    dot_lines.append('}')
    dot_content = "\n".join(dot_lines)
    
    # Render
    output_base = os.path.join(output_dir, f"star_{fact_name}")
    graph = graphviz.Source(dot_content)
    graph.render(output_base, format='png', cleanup=True)
    
    return f"{output_base}.png", len(connected_dims)


def main():
    parser = argparse.ArgumentParser(description="Generate ERD from BigQuery dataset")
    parser.add_argument("--output", default="BQ_erd_generated", help="Output directory")
    parser.add_argument("--project", default="project-534688f2-c3a9-4bff-95a", help="GCP Project ID")
    parser.add_argument("--dataset", default="netflix_dw", help="BigQuery Dataset ID")
    
    args = parser.parse_args()
    
    os.makedirs(args.output, exist_ok=True)
    
    print(f"Fetching schemas from BigQuery: {args.project}.{args.dataset}")
    
    try:
        import graphviz
    except ImportError:
        print("Error: pip install graphviz")
        return
    
    try:
        tables = fetch_bq_schemas(args.project, args.dataset)
    except Exception as e:
        print(f"Error fetching from BigQuery: {e}")
        print("Make sure you're authenticated: gcloud auth application-default login")
        return
    
    print(f"Found {len(tables)} tables")
    
    # Generate individual table schemas
    print("\n1. Generating individual table schemas...")
    for table_name, columns in sorted(tables.items()):
        is_fact = table_name.startswith("fact_")
        output_file = generate_table_erd(table_name, columns, args.output, is_fact)
        print(f"  ✓ {table_name} ({len(columns)} cols)")
    
    # Generate star schemas for each fact
    print("\n2. Generating star schema diagrams...")
    facts = {k: v for k, v in tables.items() if k.startswith("fact_")}
    for fact_name, fact_columns in sorted(facts.items()):
        output_file, dim_count = generate_star_erd(fact_name, fact_columns, tables, args.output)
        print(f"  ✓ {fact_name} → {dim_count} dims")
    
    # Generate full ERD
    print("\n3. Generating full ERD...")
    output_file = generate_full_erd(tables, args.output)
    print(f"  ✓ full_erd.png")
    
    print(f"\nAll ERDs saved to {args.output}/")


if __name__ == "__main__":
    main()

