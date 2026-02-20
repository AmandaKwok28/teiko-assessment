import sqlite3
import pandas as pd

conn = sqlite3.connect("data.db")

# query = """
# SELECT sex, response, time_from_treatment_start
# FROM samples
# WHERE LOWER(condition) = 'melanoma'
# """

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

df = pd.read_sql_query(query, conn)
print(df)

conn.close()
