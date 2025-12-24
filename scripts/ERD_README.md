# ERD Generation for Netflix Data Warehouse

## Setup

```bash
# Install system GraphViz
brew install graphviz          # macOS
# apt install graphviz         # Linux

# Install Python dependencies
pip install -r scripts/requirements.txt
```

## Usage

### Option 1: Star Schema Diagrams (Recommended)

Generate individual diagram per fact table (easier to read):

```bash
python scripts/generate_erd.py --method star-schemas --output star-schemas
```

### Option 2: Full ERD (All Tables)

```bash
python scripts/generate_erd.py --method bigquery-erd --output scripts
```

### Option 3: QuickDBD (Web Tool)

1. Copy `scripts/netflix_dw_quickdbd.txt`
2. Paste at https://www.quickdatabasediagrams.com/
3. Export as PNG/PDF

## Pre-generated Files

| Location | Files |
|----------|-------|
| `star-schemas/star_fact_*.png` | 12 star schema diagrams |
| `scripts/netflix_dw_erd.png` | Full ERD (30 tables) |
| `scripts/netflix_dw_quickdbd.txt` | QuickDBD format |

