# Immune Cell Analysis Dashboard (SQLite + Python + Streamlit)

This project loads immune cell count data from `cell-count.csv` into a SQLite database, computes relative frequencies for each immune cell population per sample, runs a responder vs non-responder comparison for a specific clinical subset, and exposes everything in an interactive Streamlit dashboard.

## Quickstart 

1. Install dependencies
```bash
pip install -r requirements.txt
```

2. Seed the database
```bash
# this creates a data.db file in the root of the project
python load_data.py
```

3. Run the dashboard
```bash
streamlit run dashboard.py
```

## Project Structure
```bash
.
├── load_data.py        # Builds SQLite schema and loads CSV data
├── analysis.py         # All database queries and statistical logic
├── dashboard.py        # Streamlit UI
├── cell-count.csv      # Input dataset
├── data.db             # Generated SQLite database (created at runtime)
├── requirements.txt
└── README.md
```

The project is intentionally split into three layers:
- Data ingestion layer (load_data.py)
- Query and analytics layer (analysis.py)
- Presentation layer (dashboard.py)

This separation keeps database logic independent from UI logic and makes the analytical functions reusable and testable without Streamlit.


## Database Schema Design

The database consists of two tables.

1. samples

One row per biological sample.

Columns:
- sample (TEXT, primary key)
- project
- subject
- condition
- age
- sex
- treatment
- response
- sample_type
- time_from_treatment_start

This table stores all metadata associated with a sample.


2. cell_counts

One row per (sample, immune cell population).

Columns:
- id (INTEGER primary key)
- sample_id (foreign key to samples.sample)
- cell_type
- count

Indexes:
- cell_counts(sample_id) for fast joins
- cell_counts(cell_type) for fast filtering by immune population


## Rationale for Schema Design

Normalization

Instead of storing five immune population columns directly inside the samples table, immune populations are stored in long format in cell_counts.

This avoids:
- column duplication
- schema changes if new populations are added
- rigid structure that does not scale

Adding a new immune population only requires inserting new rows into cell_counts, not altering the table structure.


Query Efficiency

Most analytics require:
- filtering by treatment, condition, or time
- grouping by sample
- aggregating by population

The schema supports this cleanly through:
- indexed joins on sample_id
- window functions for per-sample totals
- group-by queries for subset analysis


Scalability

If this dataset scaled to:
- hundreds of projects
- thousands of samples
- millions of population rows

the structure would still work efficiently because:

- Metadata is separated from measurements
- Joins are indexed
- Population-level analytics operate on a normalized measurement table
- New treatments like quintazide require no structural change

If analytics became more complex, additional dimension tables such as projects, subjects, or treatments could be added without breaking existing queries.


## Part 2: Relative Frequency Computation

For each sample:

- total_count is computed using a window function over cell_counts
- percentage = (count / total_count) * 100

Each output row represents one population within one sample. This preserves granularity and allows downstream analyses and visualization.


## Part 3: Statistical Analysis

The dashboard filters to:

- condition = melanoma
- treatment = miraclib
- sample_type = PBMC

For each immune population:
- A boxplot compares responders vs non-responders
- A Mann–Whitney U test evaluates statistical significance

This non-parametric test was selected because sample sizes are limited and normality cannot be assumed.

The dashboard reports p-values and flags populations where p < 0.05.


## Part 4: Baseline Subset Analysis

The following subset is extracted:

- melanoma
- miraclib
- PBMC
- time_from_treatment_start = 0

The program computes:

- number of samples per project
- number of unique subjects by response
- number of unique subjects by gender
- average B cell count for melanoma male responders at baseline, rounded to two decimals

All computations are executed directly in SQL to ensure reproducibility and efficiency.


## Code Design Decisions

### Why SQLite

- Lightweight
- Zero configuration
- Portable in GitHub Codespaces
- Suitable for analytical workloads at this scale

### Why Window Functions

Window functions allow computing per-sample totals without collapsing rows, preserving row-level granularity.

### Why Separate analysis.py

Keeping all SQL logic in one file:
- Improves readability
- Keeps dashboard.py clean
- Makes analytical functions reusable and easier to test

### Why Streamlit Instead of React + TypeScript

Although I have experience building full-stack applications using TypeScript and React for the frontend, the scope of this assignment prioritizes analytical clarity over frontend architecture. The primary goal is to surface statistically grounded insights from the data, not to engineer a production-grade UI framework.

Streamlit allows rapid iteration on data workflows, tight integration with pandas and matplotlib, and minimal overhead between querying the database and rendering results. This keeps the focus on correctness, reproducibility, and interpretability of the analysis rather than frontend state management or API design.

If this were deployed as a production analytics product, a React + TypeScript frontend backed by a REST or GraphQL API would be appropriate. For this assignment, Streamlit provides a simpler and more direct path to communicating the core findings.


## Reproducibility

To reproduce results:

```bash
pip install -r requirements.txt
python load_data.py
streamlit run dashboard.py
```

All outputs are generated dynamically from data.db.


## Dashboard Link

Deployed dashboard:

<PASTE_YOUR_STREAMLIT_LINK_HERE>