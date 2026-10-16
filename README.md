# Order Fulfillment SLA & Delay Analysis

A small, reproducible Business Analyst portfolio project that investigates order delivery performance using **synthetic data, Python, SQLite, and SQL**. The goal is to turn order timestamps into operational KPIs and identify which warehouses, carriers, or regions warrant further investigation.

## Business question

An e-commerce operations team is receiving complaints about late deliveries. Which parts of the order journey are associated with longer fulfillment times, and where should the team investigate first?

This project measures delivery performance and compares segments. It does not claim that a particular segment causes delays; findings are based on generated demonstration data and should be validated before any real operational decision.

## What it does

- Generates a reproducible synthetic dataset of 2,000 orders.
- Calculates warehouse processing, handoff, transit, and end-to-end fulfillment durations.
- Measures late-delivery rate and average fulfillment time.
- Compares performance across warehouses, carriers, and regions.
- Loads the enriched orders into a local SQLite database.
- Exports SQL-based KPI and segment summaries as CSV files.

## Tech stack

**Python 3.11+** · **pandas** · **SQLite** · **SQL**

## Project structure

```text
.
├── src/
│   ├── generate_data.py    # Generates synthetic order records
│   └── run_analysis.py    # Calculates durations and executes SQL summaries
├── sql/
│   └── analysis.sql       # Reusable KPI and segment-analysis queries
├── data/
│   ├── raw/               # Generated orders CSV (created when you run the generator)
│   └── processed/         # Local SQLite database (generated)
├── outputs/               # Exported KPI tables (generated)
├── requirements.txt
└── README.md
```

## Run on Windows

Open PowerShell in this repository folder.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.generate_data
python -m src.run_analysis
```

If activation is blocked by PowerShell policy, use the environment's Python executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.generate_data
.\.venv\Scripts\python.exe -m src.run_analysis
```

## Outputs

After running the pipeline, the project creates:

- `outputs/kpis.csv` — overall order count, late orders, late-delivery rate and fulfillment-time KPIs.
- `outputs/by_warehouse.csv` — delivery and processing metrics by warehouse.
- `outputs/by_carrier.csv` — delivery metrics by carrier.
- `outputs/by_region.csv` — delivery metrics by region.
- `data/processed/order_fulfillment.db` — local SQLite database with an `orders` table.

The generated data and output files are excluded from Git so the repository stays lightweight. Run the scripts to recreate them.

## How to interpret the analysis

1. Start with the overall late-delivery rate and average fulfillment time.
2. Compare the warehouse-processing, handoff, and transit durations.
3. Review warehouse, carrier, and region summaries to identify segments worth investigating.
4. Check sample sizes before comparing rates, and avoid treating small differences as meaningful without further analysis.
5. Validate any proposed intervention with real data and a controlled follow-up measurement.

**Important limitations:** All records are synthetic. Segment differences are descriptive, not proof of causation. The SLA threshold in the generated data is illustrative and does not represent a real company's policy.

## Original implementation

The scripts and synthetic data generator for this repository are being created from scratch for this portfolio project. No third-party project's source code or dataset is copied into this baseline. No `LICENSE` file is included.
