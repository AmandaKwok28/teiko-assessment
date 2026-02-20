import pandas as pd
from scipy.stats import mannwhitneyu


# --------------------------------------------------
# PART 2
# --------------------------------------------------

def get_relative_frequencies(conn):
    query = """
        SELECT
            s.sample,
            s.project,
            s.subject,
            s.condition,
            s.sex,
            s.treatment,
            s.response,
            s.sample_type,
            s.time_from_treatment_start,
            SUM(c.count) OVER (PARTITION BY s.sample) AS total_count,
            c.cell_type AS population,
            c.count,
            ROUND(
                (c.count * 100.0) /
                SUM(c.count) OVER (PARTITION BY s.sample),
                4
            ) AS percentage
        FROM samples s
        JOIN cell_counts c
            ON s.sample = c.sample_id
        ORDER BY s.sample, c.cell_type
    """
    return pd.read_sql_query(query, conn)


# --------------------------------------------------
# PART 3 FILTERED DATA
# --------------------------------------------------

def get_melanoma_miraclib_pbmc(conn):
    query = """
        SELECT
            s.sample,
            s.condition,
            s.response,
            s.sample_type,
            s.treatment,
            SUM(c.count) OVER (PARTITION BY s.sample) AS total_count,
            c.cell_type AS population,
            c.count,
            ROUND(
                (c.count * 100.0) /
                SUM(c.count) OVER (PARTITION BY s.sample),
                4
            ) AS percentage
        FROM samples s
        JOIN cell_counts c
            ON s.sample = c.sample_id
        WHERE LOWER(s.condition) = 'melanoma'
          AND LOWER(s.treatment) = 'miraclib'
          AND UPPER(s.sample_type) = 'PBMC'
    """
    return pd.read_sql_query(query, conn)


# --------------------------------------------------
# STATISTICAL TESTING
# --------------------------------------------------

def compute_population_statistics(filtered_df):

    results = []
    populations = filtered_df["population"].unique()

    for pop in populations:
        pop_df = filtered_df[filtered_df["population"] == pop]

        responders = pop_df[pop_df["response"].str.lower() == "yes"]["percentage"]
        non_responders = pop_df[pop_df["response"].str.lower() == "no"]["percentage"]

        if len(responders) > 0 and len(non_responders) > 0:
            stat, p_value = mannwhitneyu(responders, non_responders)
        else:
            p_value = None

        results.append({
            "population": pop,
            "p_value": p_value,
            "significant_(p<0.05)": p_value is not None and p_value < 0.05
        })

    return pd.DataFrame(results)


# --------------------------------------------------
# PART 4 BASELINE DATA
# --------------------------------------------------

def get_baseline_melanoma_pbmc(conn):
    query = """
        SELECT *
        FROM samples
        WHERE LOWER(condition) = 'melanoma'
          AND LOWER(treatment) = 'miraclib'
          AND UPPER(sample_type) = 'PBMC'
          AND time_from_treatment_start = 0
    """
    return pd.read_sql_query(query, conn)


def count_samples_by_project(conn):
    query = """
        SELECT project, COUNT(*) AS sample_count
        FROM samples
        WHERE LOWER(condition) = 'melanoma'
          AND LOWER(treatment) = 'miraclib'
          AND UPPER(sample_type) = 'PBMC'
          AND time_from_treatment_start = 0
        GROUP BY project
    """
    return pd.read_sql_query(query, conn)


def count_subjects_by_response(conn):
    query = """
        SELECT response, COUNT(DISTINCT subject) AS subject_count
        FROM samples
        WHERE LOWER(condition) = 'melanoma'
          AND LOWER(treatment) = 'miraclib'
          AND UPPER(sample_type) = 'PBMC'
          AND time_from_treatment_start = 0
        GROUP BY response
    """
    return pd.read_sql_query(query, conn)


def count_subjects_by_gender(conn):
    query = """
        SELECT sex, COUNT(DISTINCT subject) AS subject_count
        FROM samples
        WHERE LOWER(condition) = 'melanoma'
          AND LOWER(treatment) = 'miraclib'
          AND UPPER(sample_type) = 'PBMC'
          AND time_from_treatment_start = 0
        GROUP BY sex
    """
    return pd.read_sql_query(query, conn)


def avg_b_cells_male_responders(conn):
    query = """
        SELECT ROUND(AVG(
            (c.count * 100.0) /
            (SELECT SUM(count)
             FROM cell_counts
             WHERE sample_id = s.sample)
        ), 2) AS avg_b_cells
        FROM samples s
        JOIN cell_counts c
            ON s.sample = c.sample_id
        WHERE LOWER(s.condition) = 'melanoma'
          AND LOWER(s.treatment) = 'miraclib'
          AND UPPER(s.sample_type) = 'PBMC'
          AND s.time_from_treatment_start = 0
          AND UPPER(s.sex) = 'M'
          AND LOWER(s.response) = 'yes'
          AND c.cell_type = 'b_cell'
    """
    return pd.read_sql_query(query, conn)
